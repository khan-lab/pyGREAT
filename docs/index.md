# pyGREAT

**A scalable genomic region functional enrichment in Python with the GREAT framework**

[![PyPI version](https://badge.fury.io/py/pygreat.svg)](https://badge.fury.io/py/pygreat)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## What is pyGREAT?

pygreat is a Python package that provides programmatic access to [GREAT](https://great.stanford.edu/) (Genomic Regions Enrichment of Annotations Tool) from Stanford University. GREAT assigns biological meaning to a set of non-coding genomic regions by analyzing the annotations of nearby genes.

## Features

- **Multiple input formats** - Submit BED files, URLs, or pandas DataFrames
- **Batch API** - Fast results using GREAT's batch processing endpoint
- **Rich results** - Get enrichment tables as pandas DataFrames for easy analysis
- **Visualization** - Create publication-ready bar and dot plots with seaborn
- **CLI** - Beautiful command-line interface powered by rich-click
- **Type hints** - Full type annotations for IDE support and static analysis
- **Modern Python** - Built for Python 3.10+ with modern syntax

## Quick Example

```python
from pygreat import GreatClient

# Submit genomic regions and get enrichment results
client = GreatClient()
job = client.submit_job("peaks.bed", species="hg38")

# Get GO Biological Process enrichment
results = job.get_enrichment_tables()
go_bp = results["GO Biological Process"]

# Filter significant terms
significant = go_bp[go_bp["binom_fdr"] < 0.05]
print(significant[["term_name", "binom_fdr", "observed_genes"]].head(10))
```

## Command Line

```bash
# Submit and save results
pygreat submit peaks.bed --species hg38 --output results.tsv

# Create visualization
pygreat plot results.tsv -t "GO Biological Process" -o enrichment.png
```

## Installation

```bash
pip install pygreat
```

## Citation

If you use GREAT in your research, please cite:

> McLean CY, Bristor D, Hiller M, et al. GREAT improves functional interpretation of cis-regulatory regions. _Nature Biotechnology_. 2010;28(5):495-501.

## License

pygreat is released under the [MIT License](https://opensource.org/licenses/MIT).
