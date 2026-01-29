"""HTTP client with retry logic and file hosting support."""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from pygreat.core.config import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_REQUEST_INTERVAL,
    FILE_HOSTING_TIMEOUT,
    FILE_HOSTING_URL,
)
from pygreat.core.exceptions import ConnectionError, RateLimitError


class HTTPClient:
    """HTTP client with exponential backoff, rate limit handling, and file hosting.

    This client handles:
    - Uploading BED files to temporary hosting services
    - Making requests to the GREAT batch API
    - Exponential backoff retry for rate limiting

    Attributes:
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts.
        base_interval: Base interval between retries in seconds.

    Example:
        >>> client = HTTPClient(timeout=300.0)
        >>> url = client.upload_to_hosting(bed_content, "regions.bed")
        >>> response = client.get(great_url)
        >>> client.close()
    """

    def __init__(
        self,
        timeout: float = 300.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_interval: float = DEFAULT_REQUEST_INTERVAL,
    ) -> None:
        """Initialize the HTTP client.

        Args:
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retry attempts.
            base_interval: Base interval between retries in seconds.
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_interval = base_interval
        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    def upload_to_hosting(
        self,
        content: bytes,
        filename: str = "regions.bed",
    ) -> str:
        """Upload file content to a temporary hosting service.

        Uses transfer.sh for simple, no-registration file hosting.
        Files are retained for up to 14 days.

        Args:
            content: File content as bytes.
            filename: Filename for the upload.

        Returns:
            Public URL to access the uploaded file.

        Raises:
            ConnectionError: If upload fails.
        """
        upload_url = f"{FILE_HOSTING_URL}/{filename}"
        headers = {
            "User-Agent": "pygreat/1.0",
            "Content-Type": "text/plain",
        }

        for attempt in range(self.max_retries):
            try:
                # transfer.sh uses PUT with filename in URL
                response = self._client.put(
                    upload_url,
                    content=content,
                    headers=headers,
                    timeout=FILE_HOSTING_TIMEOUT,
                )
                response.raise_for_status()
                # transfer.sh returns the download URL directly
                url = response.text.strip()
                return url
            except httpx.HTTPStatusError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                raise ConnectionError(f"Failed to upload file: {e}") from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                raise ConnectionError(f"Upload request failed: {e}") from e

        raise ConnectionError("Max retries exceeded for file upload")

    def get(self, url: str, params: dict[str, Any] | None = None) -> httpx.Response:
        """GET request with retry logic.

        Args:
            url: Target URL.
            params: Optional query parameters.

        Returns:
            HTTP response.

        Raises:
            RateLimitError: If rate limit exceeded after all retries.
            ConnectionError: If connection fails after retries.
        """
        for attempt in range(self.max_retries):
            try:
                response = self._client.get(url, params=params)

                # Check for rate limit
                if self._is_rate_limited(response):
                    wait_time = self._calculate_backoff(attempt)
                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    raise RateLimitError(
                        "GREAT rate limit exceeded",
                        retry_after=wait_time,
                    )

                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = self._calculate_backoff(attempt)
                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    raise RateLimitError(str(e), retry_after=wait_time) from e
                raise ConnectionError(f"HTTP error: {e}") from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    time.sleep(wait_time)
                    continue
                raise ConnectionError(f"Request failed: {e}") from e

        raise ConnectionError("Max retries exceeded")

    def get_batch(
        self,
        base_url: str,
        request_url: str,
        species: str,
        request_name: str = "pygreat",
        request_sender: str = "pygreat",
        bg_url: str | None = None,
    ) -> str:
        """Make a GREAT batch API request.

        Args:
            base_url: GREAT API base URL with endpoint.
            request_url: Public URL to the BED file.
            species: Genome assembly (hg38, hg19, mm10, mm9).
            request_name: Name for the request.
            request_sender: Sender identifier.
            bg_url: Optional background BED file URL.

        Returns:
            TSV content from GREAT batch API.

        Raises:
            ConnectionError: If request fails.
            RateLimitError: If rate limit exceeded.
        """
        params = {
            "outputType": "batch",
            "requestURL": request_url,
            "requestSpecies": species,
            "requestName": request_name,
            "requestSender": request_sender,
        }

        if bg_url:
            params["bgURL"] = bg_url

        # Build full URL with encoded parameters
        full_url = f"{base_url}?{urlencode(params)}"
        print(f"Requesting GREAT batch API with URL: {full_url}")

        response = self.get(full_url)
        return response.text

    def _is_rate_limited(self, response: httpx.Response) -> bool:
        """Check if response indicates rate limiting.

        Args:
            response: HTTP response to check.

        Returns:
            True if rate limited, False otherwise.
        """
        if response.status_code == 429:
            return True
        text = response.text.lower()
        return "rate limit" in text or "too many requests" in text

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Wait time in seconds.
        """
        base = self.base_interval * (2 ** attempt)
        jitter = random.uniform(0, base * 0.1)
        return float(min(base + jitter, 300.0))  # Cap at 5 minutes

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> HTTPClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncHTTPClient:
    """Async HTTP client with exponential backoff, rate limit handling, and file hosting.

    This is the async version of HTTPClient, using httpx.AsyncClient.

    Example:
        >>> async with AsyncHTTPClient() as client:
        ...     url = await client.upload_to_hosting(bed_content)
        ...     response = await client.get(great_url)
    """

    def __init__(
        self,
        timeout: float = 300.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_interval: float = DEFAULT_REQUEST_INTERVAL,
    ) -> None:
        """Initialize the async HTTP client."""
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_interval = base_interval
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    async def upload_to_hosting(
        self,
        content: bytes,
        filename: str = "regions.bed",
    ) -> str:
        """Upload file content to a temporary hosting service (async).

        Args:
            content: File content as bytes.
            filename: Filename for the upload.

        Returns:
            Public URL to access the uploaded file.

        Raises:
            ConnectionError: If upload fails.
        """
        upload_url = f"{FILE_HOSTING_URL}/{filename}"
        headers = {
            "User-Agent": "pygreat/1.0",
            "Content-Type": "text/plain",
        }

        for attempt in range(self.max_retries):
            try:
                # transfer.sh uses PUT with filename in URL
                response = await self._client.put(
                    upload_url,
                    content=content,
                    headers=headers,
                    timeout=FILE_HOSTING_TIMEOUT,
                )
                response.raise_for_status()
                url = response.text.strip()
                return url
            except httpx.HTTPStatusError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    await asyncio.sleep(wait_time)
                    continue
                raise ConnectionError(f"Failed to upload file: {e}") from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    await asyncio.sleep(wait_time)
                    continue
                raise ConnectionError(f"Upload request failed: {e}") from e

        raise ConnectionError("Max retries exceeded for file upload")

    async def get(
        self, url: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        """GET request with retry logic (async).

        Args:
            url: Target URL.
            params: Optional query parameters.

        Returns:
            HTTP response.

        Raises:
            RateLimitError: If rate limit exceeded after all retries.
            ConnectionError: If connection fails after retries.
        """
        for attempt in range(self.max_retries):
            try:
                response = await self._client.get(url, params=params)

                if self._is_rate_limited(response):
                    wait_time = self._calculate_backoff(attempt)
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                    raise RateLimitError(
                        "GREAT rate limit exceeded",
                        retry_after=wait_time,
                    )

                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    wait_time = self._calculate_backoff(attempt)
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                    raise RateLimitError(str(e), retry_after=wait_time) from e
                raise ConnectionError(f"HTTP error: {e}") from e
            except httpx.RequestError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._calculate_backoff(attempt)
                    await asyncio.sleep(wait_time)
                    continue
                raise ConnectionError(f"Request failed: {e}") from e

        raise ConnectionError("Max retries exceeded")

    async def get_batch(
        self,
        base_url: str,
        request_url: str,
        species: str,
        request_name: str = "pygreat",
        request_sender: str = "pygreat",
        bg_url: str | None = None,
    ) -> str:
        """Make a GREAT batch API request (async).

        Args:
            base_url: GREAT API base URL with endpoint.
            request_url: Public URL to the BED file.
            species: Genome assembly (hg38, hg19, mm10, mm9).
            request_name: Name for the request.
            request_sender: Sender identifier.
            bg_url: Optional background BED file URL.

        Returns:
            TSV content from GREAT batch API.
        """
        params = {
            "outputType": "batch",
            "requestURL": request_url,
            "requestSpecies": species,
            "requestName": request_name,
            "requestSender": request_sender,
        }

        if bg_url:
            params["bgURL"] = bg_url

        full_url = f"{base_url}?{urlencode(params)}"
        response = await self.get(full_url)
        return response.text

    def _is_rate_limited(self, response: httpx.Response) -> bool:
        """Check if response indicates rate limiting."""
        if response.status_code == 429:
            return True
        text = response.text.lower()
        return "rate limit" in text or "too many requests" in text

    def _calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter."""
        base = self.base_interval * (2 ** attempt)
        jitter = random.uniform(0, base * 0.1)
        return float(min(base + jitter, 300.0))

    async def close(self) -> None:
        """Close the async HTTP client."""
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
