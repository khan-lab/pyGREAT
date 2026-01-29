"""Configuration and constants for pygreat."""

from typing import Final

# GREAT versions
DEFAULT_VERSION: Final[str] = "4.0.4"

# Supported species by version
SUPPORTED_SPECIES: Final[dict[str, tuple[str, ...]]] = {
    "4.0.4": ("hg38", "hg19", "mm10", "mm9"),
    "3.0.0": ("hg19", "mm10", "mm9", "danRer7"),
    "2.0.2": ("hg19", "hg18", "mm9", "danRer7"),
}

# Association rules
ASSOCIATION_RULES: Final[tuple[str, ...]] = (
    "basalPlusExt",
    "twoClosest",
    "oneClosest",
)

# Rate limiting
DEFAULT_REQUEST_INTERVAL: Final[float] = 30.0  # seconds
DEFAULT_MAX_RETRIES: Final[int] = 5
MAX_CONCURRENT_REQUESTS: Final[int] = 5  # GREAT's global limit

# Input limits
MAX_REGIONS: Final[int] = 500_000
MAX_BED_FILE_SIZE: Final[int] = 50_000_000  # 50 MB

# Default rule parameters (in kb)
DEFAULT_UPSTREAM_KB: Final[float] = 5.0
DEFAULT_DOWNSTREAM_KB: Final[float] = 1.0
DEFAULT_SPAN_KB: Final[float] = 1000.0
DEFAULT_TWO_DISTANCE_KB: Final[float] = 1000.0
DEFAULT_ONE_DISTANCE_KB: Final[float] = 1000.0

# GREAT API endpoints - Batch mode API
GREAT_BASE_URL: Final[str] = "http://great.stanford.edu/public/cgi-bin"
GREAT_BATCH_ENDPOINT: Final[str] = "greatStart.php"

# Temporary file hosting services (for uploading BED files)
# transfer.sh is a simple, no-registration file hosting service
FILE_HOSTING_URL: Final[str] = "https://transfer.sh"
FILE_HOSTING_TIMEOUT: Final[float] = 60.0  # seconds

# Default ontologies to retrieve
DEFAULT_ONTOLOGIES: Final[tuple[str, ...]] = (
    "GO Molecular Function",
    "GO Biological Process",
    "GO Cellular Component",
)

# Batch output column mappings
BATCH_COLUMN_MAP: Final[dict[str, str]] = {
    "Ontology": "ontology",
    "ID": "term_id",
    "Desc": "term_name",
    "BinomRank": "binom_rank",
    "BinomP": "binom_p",
    "BinomBonfP": "binom_bonferroni",
    "BinomFdrQ": "binom_fdr",
    "RegionFoldEnrich": "binom_fold_enrichment",
    "ExpRegions": "expected_regions",
    "ObsRegions": "observed_regions",
    "GenomeFrac": "genome_fraction",
    "SetCov": "region_coverage",
    "HyperRank": "hyper_rank",
    "HyperP": "hyper_p",
    "HyperBonfP": "hyper_bonferroni",
    "HyperFdrQ": "hyper_fdr",
    "GeneFoldEnrich": "hyper_fold_enrichment",
    "ExpGenes": "expected_genes",
    "ObsGenes": "observed_genes",
    "TotalGenes": "total_genes",
    "GeneSetCov": "gene_coverage",
    "TermCov": "term_coverage",
    "Regions": "regions",
    "Genes": "genes",
}
