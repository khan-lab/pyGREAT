# pyGREAT

[![PyPI version](https://badge.fury.io/py/pygreat.svg)](https://badge.fury.io/py/pygreat)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Programmatic Python access to [GREAT](https://great.stanford.edu/) (Genomic Regions Enrichment of Annotations Tool) from Stanford.

## Features

- Submit genomic regions (BED files, URLs, or pandas DataFrames) to GREAT
- Retrieve enrichment results as pandas DataFrames
- Visualize top enriched terms with seaborn bar/dot plots
- Beautiful CLI powered by rich-click
- Full type hints and modern Python 3.10+ syntax

## Installation

```bash
pip install py-great
```

Or install from source:

```bash
git clone https://github.com/khan-lab/pyGREAT.git
cd pygreat
pip install -e .
```

## Quick Start

### Python API

```python
from pygreat import GreatClient

# Create client and submit job
client = GreatClient()
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    rule="basalPlusExt",
)

# Get enrichment results
results = job.get_enrichment_tables()

# Access GO Biological Process results
go_bp = results["GO Biological Process"]
print(go_bp.head())

# Visualize top terms
from pygreat.viz import plot_enrichment_bar

significant = go_bp[go_bp["binom_fdr"] < 0.05]
fig, ax = plot_enrichment_bar(significant, n_terms=15)
fig.savefig("enrichment.png", dpi=300, bbox_inches="tight")
```

### From a URL

If your BED file is publicly accessible, you can pass the URL directly without any file upload:

```python
from pygreat import GreatClient

client = GreatClient()
job = client.submit_job(
    "https://asntech.org/dbsuper/data/bed/hg19/Astrocytes.bed",  # Direct URL - no upload needed
    species="hg19",
)
results = job.get_enrichment_tables()
```

### From a DataFrame

```python
import pandas as pd
from pygreat import GreatClient

# Your genomic regions as a DataFrame
regions = pd.DataFrame({
    "chrom": ["chr1", "chr1", "chr2"],
    "start": [1000, 5000, 10000],
    "end": [2000, 6000, 11000],
})

client = GreatClient()
job = client.submit_job(regions, species="hg38")
results = job.get_enrichment_tables()
```

### Context Manager

```python
from pygreat import GreatClient

with GreatClient() as client:
    job = client.submit_job("peaks.bed", species="hg38")
    results = job.get_enrichment_tables()
    # Client is automatically closed when exiting the block
```

### Command Line Interface

```bash
# Submit job and save results
pygreat submit peaks.bed --species hg38 --output results.tsv

# Submit from a URL (no upload needed)
pygreat submit https://example.com/peaks.bed --species hg38 -o results.tsv

# With background regions
pygreat submit peaks.bed -s hg38 -b background.bed -o results.tsv

# Filter by FDR and minimum genes
pygreat submit peaks.bed --max-fdr 0.01 --min-genes 5 -o results.tsv

# Verbose mode to see progress
pygreat -v submit peaks.bed -s hg38 -o results.tsv

# Create visualization
pygreat plot results.tsv -t "GO Biological Process" -o enrichment.png

# Dot plot with custom number of terms
pygreat plot results.tsv -t "GO Biological Process" --plot-type dot -n 20 -o dotplot.png
```

## Supported Species

GREAT v4.0.4 supports:

- Human: `hg38`, `hg19`
- Mouse: `mm10`, `mm9`

## Association Rules

- `basalPlusExt` (default): Basal regulatory domain with extension (5kb upstream, 1kb downstream, 1Mb max extension)
- `twoClosest`: Extends to nearest two genes' TSS
- `oneClosest`: Extends to midpoint of nearest gene's TSS

## API Reference

### GreatClient

```python
from pygreat import GreatClient

client = GreatClient(
    base_url=None,           # Custom GREAT server URL
    version="4.0.4",         # GREAT version
    request_interval=30.0,   # Seconds between retries
    max_retries=5,           # Maximum retry attempts
    timeout=300.0,           # Request timeout in seconds
)
```

### submit_job()

```python
job = client.submit_job(
    regions,                 # BED file path, URL, DataFrame, or GenomicRegions
    species="hg38",          # Genome assembly
    background=None,         # Optional background regions (path, URL, or DataFrame)
    rule="basalPlusExt",     # Association rule
    job_name=None,           # Optional job identifier
    zero_based=False,        # True if input coordinates are 0-based (BED standard)
)
```

**Input formats:**

- Local BED file path: `"peaks.bed"` or `Path("peaks.bed")`
- URL to public BED file: `"https://example.com/peaks.bed"`
- pandas DataFrame with `chrom`, `start`, `end` columns
- `GenomicRegions` object

### GreatJob

```python
# Get enrichment tables for all ontologies
results = job.get_enrichment_tables()

# Get specific ontologies with filtering
results = job.get_enrichment_tables(
    ontologies=["GO Biological Process", "GO Molecular Function"],
    min_genes=5,        # Minimum genes per term
    max_fdr=0.05,       # Maximum FDR threshold
)

# Get single ontology
go_bp = job.get_enrichment_table("GO Biological Process", max_fdr=0.05)

# List available ontologies
ontologies = job.list_ontologies()
# ['GO Biological Process', 'GO Molecular Function', 'GO Cellular Component', ...]

# Get categorized ontologies
categories = job.available_ontologies()
# {'Gene Ontology': ['GO Biological Process', ...], 'Pathway Data': [...], ...}

# Get job metadata
metadata = job.get_metadata()
# {'version': '4.0.4', 'species': 'hg38', 'rule': 'Basal+extension: ...'}

# Export to single DataFrame (with ontology column)
df = job.to_dataframe()
df.to_csv("all_results.tsv", sep="\t", index=False)

# Export single ontology
df = job.to_dataframe("GO Biological Process")
```

### Enrichment DataFrame Columns

Each enrichment table contains these columns:

| Column                  | Description                                  |
| ----------------------- | -------------------------------------------- |
| `term_id`               | Ontology term identifier (e.g., GO:0006915)  |
| `term_name`             | Human-readable term name                     |
| `binom_rank`            | Binomial test rank                           |
| `binom_p`               | Binomial raw p-value                         |
| `binom_fdr`             | Binomial FDR-corrected q-value               |
| `binom_fold_enrichment` | Binomial fold enrichment                     |
| `observed_regions`      | Number of input regions associated with term |
| `expected_regions`      | Expected regions under null                  |
| `hyper_rank`            | Hypergeometric test rank                     |
| `hyper_p`               | Hypergeometric raw p-value                   |
| `hyper_fdr`             | Hypergeometric FDR-corrected q-value         |
| `hyper_fold_enrichment` | Hypergeometric fold enrichment               |
| `observed_genes`        | Number of genes in input regions             |
| `expected_genes`        | Expected genes under null                    |
| `total_genes`           | Total genes annotated to term                |

## Visualization

### Bar Plot

```python
from pygreat.viz import plot_enrichment_bar

fig, ax = plot_enrichment_bar(
    df,                      # Enrichment DataFrame
    n_terms=15,              # Number of top terms to show
    pvalue_col="binom_fdr",  # Column for significance
    name_col="term_name",    # Column for term names
    title="GO Biological Process",
    figsize=(10, 8),
)
fig.savefig("barplot.png", dpi=300, bbox_inches="tight")
```

### Dot Plot

```python
from pygreat.viz import plot_enrichment_dot

fig, ax = plot_enrichment_dot(
    df,
    n_terms=15,
    pvalue_col="binom_fdr",
    size_col="observed_genes",   # Column for dot size
    name_col="term_name",
    title="GO Biological Process",
    figsize=(10, 8),
)
fig.savefig("dotplot.png", dpi=300, bbox_inches="tight")
```

## Error Handling

```python
from pygreat import GreatClient
from pygreat.core.exceptions import (
    GreatError,
    InvalidSpeciesError,
    RateLimitError,
    ParsingError,
)

try:
    client = GreatClient()
    job = client.submit_job("peaks.bed", species="hg38")
except InvalidSpeciesError as e:
    print(f"Invalid species: {e}")
except RateLimitError as e:
    print(f"Rate limited: {e}")
except GreatError as e:
    print(f"GREAT error: {e}")
```

## Rate Limiting

GREAT limits concurrent requests globally. pygreat handles this automatically with exponential backoff:

- Base interval: 30 seconds
- Max wait: 5 minutes
- Max retries: 5 attempts

You can customize these:

```python
client = GreatClient(
    request_interval=60.0,  # Start with 60s between retries
    max_retries=10,         # Try up to 10 times
)
```

## Citation

If you use GREAT in your research, please cite:

> McLean CY, Bristor D, Hiller M, et al. GREAT improves functional interpretation of cis-regulatory regions. _Nature Biotechnology_. 2010;28(5):495-501.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [GREAT](https://great.stanford.edu/) by the Bejerano Lab at Stanford
- [rGREAT](https://github.com/jokergoo/rGREAT) R package for inspiration
