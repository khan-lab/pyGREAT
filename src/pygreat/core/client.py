"""Main GREAT client for submitting jobs and retrieving results."""

from __future__ import annotations

from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import pandas as pd

from pygreat.api.http import HTTPClient
from pygreat.api.parser import BatchResponseParser
from pygreat.core.config import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_REQUEST_INTERVAL,
    DEFAULT_VERSION,
    GREAT_BASE_URL,
    GREAT_BATCH_ENDPOINT,
    SUPPORTED_SPECIES,
)
from pygreat.core.exceptions import InvalidSpeciesError
from pygreat.core.job import GreatJob
from pygreat.models.regions import GenomicRegions

Species = Literal["hg38", "hg19", "mm10", "mm9"]
AssociationRule = Literal["basalPlusExt", "twoClosest", "oneClosest"]


def _is_url(path: str) -> bool:
    """Check if a string is a valid URL."""
    try:
        result = urlparse(path)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except (ValueError, AttributeError):
        return False


class GreatClient:
    """Client for interacting with the GREAT web service.

    This client uses the GREAT batch API to submit regions and retrieve
    enrichment results in a single request.

    Attributes:
        base_url: The base URL for the GREAT API.
        version: GREAT version to use (default: 4.0.4).
        request_interval: Seconds between retry attempts.
        max_retries: Maximum number of retry attempts.

    Example:
        >>> from pygreat import GreatClient
        >>> client = GreatClient()
        >>> job = client.submit_job("peaks.bed", species="hg38")
        >>> results = job.get_enrichment_tables()
        >>> print(results["GO Biological Process"].head())
    """

    def __init__(
        self,
        base_url: str | None = None,
        version: str = DEFAULT_VERSION,
        request_interval: float = DEFAULT_REQUEST_INTERVAL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float = 300.0,
    ) -> None:
        """Initialize the GREAT client.

        Args:
            base_url: Custom base URL for GREAT server.
            version: GREAT version (4.0.4, 3.0.0, or 2.0.2).
            request_interval: Seconds between polling attempts.
            max_retries: Maximum retry attempts for rate limiting.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or GREAT_BASE_URL
        self.version = version
        self.request_interval = request_interval
        self.max_retries = max_retries
        self.timeout = timeout
        self._http = HTTPClient(
            timeout=timeout,
            max_retries=max_retries,
            base_interval=request_interval,
        )
        self._parser = BatchResponseParser()

    def submit_job(
        self,
        regions: str | Path | pd.DataFrame | GenomicRegions,
        species: Species = "hg38",
        *,
        background: str | Path | pd.DataFrame | GenomicRegions | None = None,
        rule: AssociationRule = "basalPlusExt",
        job_name: str | None = None,
        zero_based: bool = False,
    ) -> GreatJob:
        """Submit a GREAT job for enrichment analysis.

        This method accepts a URL to a public BED file, or uploads a local
        BED file to a temporary hosting service, then calls the GREAT batch
        API and returns results immediately.

        Args:
            regions: Input genomic regions as:
                - URL to a public BED file (http/https)
                - Local BED file path
                - pandas DataFrame with genomic regions
                - GenomicRegions object
            species: Genome assembly (hg38, hg19, mm10, mm9).
            background: Optional background regions for foreground/background test.
                Can also be a URL or local file.
            rule: Gene association rule:
                - basalPlusExt: Basal regulatory domain with extension (default)
                - twoClosest: Extends to nearest two genes' TSS
                - oneClosest: Extends to midpoint of nearest gene's TSS
            job_name: Optional job identifier.
            zero_based: True if input coordinates are 0-based (BED standard).
                Set to False if coordinates are 1-based.

        Returns:
            GreatJob object with enrichment results.

        Raises:
            InvalidSpeciesError: If species is not supported.
            RateLimitError: If rate limit is exceeded after retries.
            ConnectionError: For network/server errors.

        Example:
            >>> client = GreatClient()
            >>> # From URL (no upload needed)
            >>> job = client.submit_job("https://example.com/peaks.bed", species="hg38")
            >>> # From local BED file
            >>> job = client.submit_job("peaks.bed", species="hg38")
            >>> # From DataFrame
            >>> df = pd.DataFrame({"chrom": ["chr1"], "start": [1000], "end": [2000]})
            >>> job = client.submit_job(df, species="hg38")
        """
        # Validate species
        supported = SUPPORTED_SPECIES.get(self.version, SUPPORTED_SPECIES["4.0.4"])
        if species not in supported:
            raise InvalidSpeciesError(
                f"Species '{species}' not supported in GREAT v{self.version}. "
                f"Supported: {supported}"
            )

        # Check if regions is a URL - use directly without upload
        if isinstance(regions, str) and _is_url(regions):
            request_url = regions
        else:
            # Convert input to GenomicRegions and upload
            genomic_regions = self._normalize_regions(regions, zero_based)
            bed_content = genomic_regions.to_bed(gzip_compress=False)
            request_url = self._http.upload_to_hosting(bed_content, "regions.bed")

        # Handle background regions if provided
        bg_url: str | None = None
        if background is not None:
            # Check if background is a URL
            if isinstance(background, str) and _is_url(background):
                bg_url = background
            else:
                bg_regions = self._normalize_regions(background, zero_based)
                bg_content = bg_regions.to_bed(gzip_compress=False)
                bg_url = self._http.upload_to_hosting(bg_content, "background.bed")

        # Call batch API
        batch_endpoint = f"{self.base_url}/{GREAT_BATCH_ENDPOINT}"
        tsv_content = self._http.get_batch(
            base_url=batch_endpoint,
            request_url=request_url,
            species=species,
            request_name=job_name or "pygreat",
            request_sender="pygreat",
            bg_url=bg_url,
        )

        # Parse TSV response
        enrichment_results = self._parser.parse(tsv_content)
        metadata = self._parser.parse_metadata(tsv_content)
        ontology_stats = self._parser.parse_ontology_stats(tsv_content)

        # Build ontologies dict from results
        ontologies: dict[str, list[str]] = {}
        for ont_name in enrichment_results.keys():
            # Categorize ontologies
            if "GO" in ont_name:
                category = "Gene Ontology"
            elif "Pathway" in ont_name or "KEGG" in ont_name:
                category = "Pathway Data"
            elif "Phenotype" in ont_name:
                category = "Phenotype Data"
            elif "Disease" in ont_name:
                category = "Disease Ontology"
            else:
                category = "Other"

            if category not in ontologies:
                ontologies[category] = []
            ontologies[category].append(ont_name)

        return GreatJob(
            job_id=request_url,  # Use the file URL as job ID
            client=self,
            ontologies=ontologies,
            species=species,
            rule=rule,
            job_name=job_name,
            enrichment_results=enrichment_results,
            metadata=metadata,
            ontology_stats=ontology_stats,
        )

    def _normalize_regions(
        self,
        regions: str | Path | pd.DataFrame | GenomicRegions,
        zero_based: bool,
    ) -> GenomicRegions:
        """Convert various input formats to GenomicRegions.

        Args:
            regions: Input in various formats.
            zero_based: Whether coordinates are 0-based.

        Returns:
            GenomicRegions instance.

        Raises:
            TypeError: If input type is not supported.
        """
        if isinstance(regions, GenomicRegions):
            return regions
        if isinstance(regions, pd.DataFrame):
            return GenomicRegions.from_dataframe(regions, zero_based=zero_based)
        if isinstance(regions, (str, Path)):
            return GenomicRegions.from_bed(regions, zero_based=zero_based)
        raise TypeError(f"Unsupported regions type: {type(regions)}")

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._http.close()

    def __enter__(self) -> GreatClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
