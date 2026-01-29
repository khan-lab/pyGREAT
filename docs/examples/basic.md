# Basic Usage Examples

This page provides complete examples for common pygreat use cases.

## Example 1: Simple Enrichment Analysis

Submit a BED file and get enrichment results.

```python
from pygreat import GreatClient

# Create client
client = GreatClient()

# Submit job
job = client.submit_job("peaks.bed", species="hg38")

# Get all results
results = job.get_enrichment_tables()

# Print summary
for ontology, df in results.items():
    n_sig = (df["binom_fdr"] < 0.05).sum()
    print(f"{ontology}: {n_sig} significant terms")

# Access GO Biological Process
go_bp = results["GO Biological Process"]

# Show top 10 terms
top10 = go_bp.nsmallest(10, "binom_fdr")
print(top10[["term_name", "binom_fdr", "observed_genes"]])

# Clean up
client.close()
```

## Example 2: From a DataFrame

Analyze regions from a pandas DataFrame.

```python
import pandas as pd
from pygreat import GreatClient

# Create regions DataFrame
regions = pd.DataFrame({
    "chrom": ["chr1", "chr1", "chr2", "chr3", "chr5"],
    "start": [1000000, 5000000, 10000000, 15000000, 20000000],
    "end": [1001000, 5001000, 10001000, 15001000, 20001000],
    "name": ["peak1", "peak2", "peak3", "peak4", "peak5"],
})

# Submit and analyze
with GreatClient() as client:
    job = client.submit_job(regions, species="hg38")
    results = job.get_enrichment_tables(max_fdr=0.05)

    # Check results
    if results:
        for ont, df in results.items():
            if not df.empty:
                print(f"\n{ont}:")
                print(df[["term_name", "binom_fdr"]].head())
```

## Example 3: From a URL

Analyze a publicly accessible BED file.

```python
from pygreat import GreatClient

# URL to a public BED file (no upload needed)
url = "https://example.com/data/chipseq_peaks.bed"

with GreatClient() as client:
    job = client.submit_job(url, species="hg38")
    results = job.get_enrichment_tables()

    # Process results
    go_bp = results.get("GO Biological Process")
    if go_bp is not None:
        significant = go_bp[go_bp["binom_fdr"] < 0.05]
        print(f"Found {len(significant)} significant GO terms")
```

## Example 4: With Background Regions

Perform foreground/background analysis.

```python
from pygreat import GreatClient

# Foreground: your peaks of interest
# Background: all possible peaks (e.g., from different conditions)

with GreatClient() as client:
    job = client.submit_job(
        "treatment_peaks.bed",
        species="hg38",
        background="all_accessible_regions.bed",
    )

    results = job.get_enrichment_tables(max_fdr=0.05)

    # This tests enrichment relative to background,
    # not the whole genome
```

## Example 5: Filter and Export

Filter results and save to files.

```python
from pygreat import GreatClient

with GreatClient() as client:
    job = client.submit_job("peaks.bed", species="hg38")

    # Get filtered results
    results = job.get_enrichment_tables(
        max_fdr=0.05,
        min_genes=5,
    )

    # Export all results to single TSV
    df = job.to_dataframe()
    df.to_csv("all_results.tsv", sep="\t", index=False)

    # Export each ontology separately
    for ontology, df in results.items():
        if not df.empty:
            # Create safe filename
            filename = ontology.replace(" ", "_").lower() + ".tsv"
            df.to_csv(filename, sep="\t", index=False)
            print(f"Saved {len(df)} terms to {filename}")
```

## Example 6: Simple Visualization

Create a bar plot of enrichment results.

```python
from pygreat import GreatClient
from pygreat.viz import plot_enrichment_bar

# Get results
client = GreatClient()
job = client.submit_job("peaks.bed", species="hg38")
results = job.get_enrichment_tables()
client.close()

# Get significant GO terms
go_bp = results["GO Biological Process"]
significant = go_bp[go_bp["binom_fdr"] < 0.05]

# Create plot
fig, ax = plot_enrichment_bar(
    significant,
    n_terms=15,
    title="GO Biological Process Enrichment",
)

# Save
fig.savefig("enrichment.png", dpi=300, bbox_inches="tight")
print("Saved enrichment.png")
```

## Example 7: Different Species

Analyze mouse data.

```python
from pygreat import GreatClient

# Mouse mm10 assembly
with GreatClient() as client:
    job = client.submit_job(
        "mouse_peaks.bed",
        species="mm10",
    )

    results = job.get_enrichment_tables()

    # Check metadata
    meta = job.get_metadata()
    print(f"Species: {meta['species']}")
    print(f"GREAT version: {meta['version']}")
```

## Example 8: Different Association Rules

Compare different gene association rules.

```python
from pygreat import GreatClient

rules = ["basalPlusExt", "twoClosest", "oneClosest"]

with GreatClient() as client:
    for rule in rules:
        job = client.submit_job(
            "peaks.bed",
            species="hg38",
            rule=rule,
        )

        results = job.get_enrichment_tables(max_fdr=0.05)
        go_bp = results.get("GO Biological Process")

        n_terms = len(go_bp) if go_bp is not None else 0
        print(f"{rule}: {n_terms} significant GO BP terms")
```

## Example 9: Error Handling

Handle common errors gracefully.

```python
from pygreat import GreatClient
from pygreat.core.exceptions import (
    InvalidSpeciesError,
    RateLimitError,
    GreatError,
)

def analyze_peaks(bed_file, species):
    """Analyze peaks with error handling."""
    client = GreatClient()

    try:
        job = client.submit_job(bed_file, species=species)
        return job.get_enrichment_tables()

    except InvalidSpeciesError:
        print(f"Error: '{species}' is not a valid species.")
        print("Valid options: hg38, hg19, mm10, mm9")
        return None

    except RateLimitError:
        print("Error: GREAT server is busy. Try again later.")
        return None

    except GreatError as e:
        print(f"Error: {e}")
        return None

    finally:
        client.close()

# Use it
results = analyze_peaks("peaks.bed", "hg38")
if results:
    print("Analysis complete!")
```

## Example 10: Complete Workflow

A complete analysis script.

```python
#!/usr/bin/env python3
"""Complete GREAT enrichment analysis."""

from pathlib import Path
from pygreat import GreatClient
from pygreat.viz import plot_enrichment_bar, plot_enrichment_dot


def main():
    # Configuration
    bed_file = "peaks.bed"
    species = "hg38"
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    # Run analysis
    print(f"Analyzing {bed_file}...")

    with GreatClient() as client:
        job = client.submit_job(bed_file, species=species)

        # Get filtered results
        results = job.get_enrichment_tables(max_fdr=0.05, min_genes=3)

        # Save results
        df = job.to_dataframe()
        df.to_csv(output_dir / "all_results.tsv", sep="\t", index=False)
        print(f"Saved results to {output_dir / 'all_results.tsv'}")

        # Create visualizations for GO terms
        for ont in ["GO Biological Process", "GO Molecular Function"]:
            ont_df = results.get(ont)
            if ont_df is not None and not ont_df.empty:
                # Bar plot
                fig, ax = plot_enrichment_bar(ont_df, n_terms=15, title=ont)
                filename = ont.replace(" ", "_").lower() + "_bar.png"
                fig.savefig(output_dir / filename, dpi=300, bbox_inches="tight")
                print(f"Saved {filename}")

                # Dot plot
                fig, ax = plot_enrichment_dot(ont_df, n_terms=15, title=ont)
                filename = ont.replace(" ", "_").lower() + "_dot.png"
                fig.savefig(output_dir / filename, dpi=300, bbox_inches="tight")
                print(f"Saved {filename}")

    print("Done!")


if __name__ == "__main__":
    main()
```
