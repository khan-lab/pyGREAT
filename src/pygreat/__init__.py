"""
pygreat - Programmatic access to GREAT (Genomic Regions Enrichment of Annotations Tool).

This package provides a Python interface to submit genomic regions to the
Stanford GREAT web service and retrieve functional enrichment results.

For online analysis (Stanford server):
    >>> from pygreat import GreatClient
    >>> client = GreatClient()
    >>> job = client.submit_job("peaks.bed", species="hg38")
    >>> results = job.get_enrichment_tables()

For local/offline analysis (any organism):
    >>> from pygreat.local import LocalGreat
    >>> from pygreat.local.genes import GeneAnnotation
    >>> from pygreat.local.genesets import GeneSetCollection
    >>> genes = GeneAnnotation.from_gtf("genes.gtf")
    >>> go_bp = GeneSetCollection.from_gmt("go_bp.gmt")
    >>> great = LocalGreat(genes, {"GO BP": go_bp})
    >>> result = great.analyze("peaks.bed")
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
from pygreat.local.great import LocalGreat

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "GreatClient",
    "GreatJob",
    "GenomicRegions",
    "GenomicRegion",
    # Local analysis
    "LocalGreat",
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
