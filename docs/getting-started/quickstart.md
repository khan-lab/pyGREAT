# Quick Start

This guide will help you get started with pygreat in just a few minutes.

## Basic Workflow

The typical pygreat workflow is:

1. Create a `GreatClient`
2. Submit genomic regions with `submit_job()`
3. Retrieve enrichment results
4. Analyze or visualize the results

## From a BED File

The most common use case is submitting a local BED file:

```python
from pygreat import GreatClient

# Create client
client = GreatClient()

# Submit job
job = client.submit_job(
    "peaks.bed",      # Your BED file
    species="hg38",   # Genome assembly
)

# Get all enrichment results
results = job.get_enrichment_tables()

# Access specific ontology
go_bp = results["GO Biological Process"]
print(go_bp.head())
```

## From a URL

If your BED file is publicly accessible online, you can use the URL directly (no file upload needed):

```python
from pygreat import GreatClient

client = GreatClient()
job = client.submit_job(
    "https://example.com/peaks.bed",
    species="hg38",
)
results = job.get_enrichment_tables()
```

## From a DataFrame

You can also submit regions directly from a pandas DataFrame:

```python
import pandas as pd
from pygreat import GreatClient

# Create regions DataFrame
regions = pd.DataFrame({
    "chrom": ["chr1", "chr1", "chr2", "chr3"],
    "start": [1000, 5000, 10000, 15000],
    "end": [2000, 6000, 11000, 16000],
})

client = GreatClient()
job = client.submit_job(regions, species="hg38")
results = job.get_enrichment_tables()
```

## Filter Significant Terms

Filter results by FDR threshold and minimum gene count:

```python
# Get results with filtering
results = job.get_enrichment_tables(
    max_fdr=0.05,      # FDR < 0.05
    min_genes=5,       # At least 5 genes
)

# Or filter after retrieval
go_bp = results["GO Biological Process"]
significant = go_bp[go_bp["binom_fdr"] < 0.05]
```

## Visualize Results

Create a bar plot of the top enriched terms:

```python
from pygreat.viz import plot_enrichment_bar

# Get significant GO terms
go_bp = results["GO Biological Process"]
significant = go_bp[go_bp["binom_fdr"] < 0.05]

# Create bar plot
fig, ax = plot_enrichment_bar(
    significant,
    n_terms=15,
    title="GO Biological Process Enrichment",
)
fig.savefig("enrichment.png", dpi=300, bbox_inches="tight")
```

## Export Results

Save results to a TSV file:

```python
# Export all ontologies (adds 'ontology' column)
df = job.to_dataframe()
df.to_csv("all_results.tsv", sep="\t", index=False)

# Export single ontology
go_bp = job.to_dataframe("GO Biological Process")
go_bp.to_csv("go_bp_results.tsv", sep="\t", index=False)
```

## Using the CLI

For quick analysis, use the command-line interface:

```bash
# Submit job and save results
pygreat submit peaks.bed --species hg38 --output results.tsv

# Filter by FDR
pygreat submit peaks.bed -s hg38 --max-fdr 0.05 -o results.tsv

# Create visualization
pygreat plot results.tsv -t "GO Biological Process" -o plot.png
```

## Context Manager

Use the context manager pattern to ensure proper cleanup:

```python
from pygreat import GreatClient

with GreatClient() as client:
    job = client.submit_job("peaks.bed", species="hg38")
    results = job.get_enrichment_tables()
    # Process results...
# Client is automatically closed
```

## Next Steps

- Learn about [different input formats](../guide/submitting-jobs.md)
- Explore [working with results](../guide/results.md)
- Create [visualizations](../guide/visualization.md)
- See the full [API reference](../api/client.md)
