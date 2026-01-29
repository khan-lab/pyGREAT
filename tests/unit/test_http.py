"""Tests for HTTPClient."""

import pytest

from pygreat.api.http import HTTPClient


class TestHTTPClient:
    """Tests for HTTPClient class."""

    @pytest.fixture
    def client(self) -> HTTPClient:
        """Create HTTP client instance."""
        return HTTPClient(timeout=10.0, max_retries=3, base_interval=1.0)

    def test_init(self, client: HTTPClient) -> None:
        """Test client initialization."""
        assert client.timeout == 10.0
        assert client.max_retries == 3
        assert client.base_interval == 1.0

    def test_calculate_backoff(self, client: HTTPClient) -> None:
        """Test exponential backoff calculation."""
        # First attempt: ~1s (base_interval)
        wait_0 = client._calculate_backoff(0)
        assert 0.9 <= wait_0 <= 1.1

        # Second attempt: ~2s (2^1 * base)
        wait_1 = client._calculate_backoff(1)
        assert 1.8 <= wait_1 <= 2.2

        # Third attempt: ~4s (2^2 * base)
        wait_2 = client._calculate_backoff(2)
        assert 3.6 <= wait_2 <= 4.4

    def test_calculate_backoff_capped(self, client: HTTPClient) -> None:
        """Test backoff is capped at 5 minutes."""
        wait = client._calculate_backoff(20)  # Would be huge without cap
        assert wait <= 300.0

    def test_is_rate_limited_status_code(self, client: HTTPClient) -> None:
        """Test rate limit detection by status code."""
        # Create a mock response
        class MockResponse:
            status_code = 429
            text = ""

        assert client._is_rate_limited(MockResponse())

    def test_is_rate_limited_text(self, client: HTTPClient) -> None:
        """Test rate limit detection by response text."""

        class MockResponse:
            status_code = 200
            text = "Error: rate limit exceeded"

        assert client._is_rate_limited(MockResponse())

    def test_context_manager(self) -> None:
        """Test context manager usage."""
        with HTTPClient() as client:
            assert client is not None
        # Client should be closed after context

    def test_close(self, client: HTTPClient) -> None:
        """Test client close."""
        client.close()
        # Should not raise


class TestAsyncHTTPClient:
    """Tests for AsyncHTTPClient class."""

    def test_import(self) -> None:
        """Test AsyncHTTPClient can be imported."""
        from pygreat.api.http import AsyncHTTPClient

        client = AsyncHTTPClient(timeout=10.0, max_retries=3, base_interval=1.0)
        assert client.timeout == 10.0
        assert client.max_retries == 3
        assert client.base_interval == 1.0

    def test_calculate_backoff(self) -> None:
        """Test async client backoff calculation."""
        from pygreat.api.http import AsyncHTTPClient

        client = AsyncHTTPClient(base_interval=1.0)

        # First attempt
        wait_0 = client._calculate_backoff(0)
        assert 0.9 <= wait_0 <= 1.1

        # Second attempt
        wait_1 = client._calculate_backoff(1)
        assert 1.8 <= wait_1 <= 2.2
