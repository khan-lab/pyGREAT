"""
pygreat - Programmatic access to GREAT (Genomic Regions Enrichment of Annotations Tool).

This package provides a Python interface to submit genomic regions to the
Stanford GREAT web service and retrieve functional enrichment results.

Example:
    >>> from pygreat import GreatClient
    >>> client = GreatClient()
    >>> job = client.submit_job("peaks.bed", species="hg38")
    >>> results = job.get_enrichment_tables()
"""

from pygreat.core.client import GreatClient
from pygreat.core.job import GreatJob
from pygreat.core.exceptions import (
    GreatError,
    InvalidSpeciesError,
    InvalidRegionsError,
    RateLimitError,
    JobNotFoundError,
    ParsingError,
    ConnectionError,
)
from pygreat.models.regions import GenomicRegions, GenomicRegion

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "GreatClient",
    "GreatJob",
    "GenomicRegions",
    "GenomicRegion",
    # Exceptions
    "GreatError",
    "InvalidSpeciesError",
    "InvalidRegionsError",
    "RateLimitError",
    "JobNotFoundError",
    "ParsingError",
    "ConnectionError",
    # Version
    "__version__",
]
