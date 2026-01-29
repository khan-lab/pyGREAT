# Advanced Usage Examples

This page covers advanced usage patterns for pygreat.

## Example 1: Batch Processing Multiple Samples

Process multiple BED files in sequence.

```python
from pathlib import Path
import pandas as pd
from pygreat import GreatClient


def process_samples(sample_dir, species="hg38"):
    """Process all BED files in a directory."""
    sample_dir = Path(sample_dir)
    results = {}

    with GreatClient() as client:
        for bed_file in sample_dir.glob("*.bed"):
            sample_name = bed_file.stem
            print(f"Processing {sample_name}...")

            job = client.submit_job(bed_file, species=species)
            sample_results = job.get_enrichment_tables(max_fdr=0.05)

            results[sample_name] = sample_results

    return results


# Process all samples
all_results = process_samples("samples/", species="hg38")

# Combine GO BP results across samples
combined = []
for sample, results in all_results.items():
    go_bp = results.get("GO Biological Process")
    if go_bp is not None and not go_bp.empty:
        go_bp = go_bp.copy()
        go_bp["sample"] = sample
        combined.append(go_bp)

if combined:
    combined_df = pd.concat(combined, ignore_index=True)
    combined_df.to_csv("combined_go_bp.tsv", sep="\t", index=False)
```

## Example 2: Comparison Across Conditions

Compare enrichment between two conditions.

```python
import numpy as np
import pandas as pd
from pygreat import GreatClient


def get_top_terms(df, n=20):
    """Get top N terms by significance."""
    return set(df.nsmallest(n, "binom_fdr")["term_name"])


# Run GREAT for two conditions
with GreatClient() as client:
    job_ctrl = client.submit_job("control_peaks.bed", species="hg38")
    job_treat = client.submit_job("treatment_peaks.bed", species="hg38")

    ctrl_results = job_ctrl.get_enrichment_tables()
    treat_results = job_treat.get_enrichment_tables()

# Get GO BP results
ctrl_bp = ctrl_results["GO Biological Process"]
treat_bp = treat_results["GO Biological Process"]

# Find top terms from both
top_terms = get_top_terms(ctrl_bp, 30) | get_top_terms(treat_bp, 30)

# Create comparison table
comparison = []
for term in top_terms:
    ctrl_row = ctrl_bp[ctrl_bp["term_name"] == term]
    treat_row = treat_bp[treat_bp["term_name"] == term]

    comparison.append({
        "term_name": term,
        "control_fdr": ctrl_row["binom_fdr"].values[0] if len(ctrl_row) else 1.0,
        "treatment_fdr": treat_row["binom_fdr"].values[0] if len(treat_row) else 1.0,
        "control_genes": ctrl_row["observed_genes"].values[0] if len(ctrl_row) else 0,
        "treatment_genes": treat_row["observed_genes"].values[0] if len(treat_row) else 0,
    })

comparison_df = pd.DataFrame(comparison)
comparison_df["log2_fc"] = np.log2(
    (comparison_df["treatment_genes"] + 1) / (comparison_df["control_genes"] + 1)
)

# Sort by difference
comparison_df = comparison_df.sort_values("log2_fc", ascending=False)
print(comparison_df.head(20))
```

## Example 3: Enrichment Heatmap

Create a heatmap across multiple samples.

```python
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pygreat import GreatClient


def run_great(client, bed_file, species):
    """Run GREAT and return GO BP results."""
    job = client.submit_job(bed_file, species=species)
    results = job.get_enrichment_tables()
    return results.get("GO Biological Process")


# Sample files
samples = {
    "Sample_A": "sampleA.bed",
    "Sample_B": "sampleB.bed",
    "Sample_C": "sampleC.bed",
    "Sample_D": "sampleD.bed",
}

# Run GREAT for all samples
with GreatClient() as client:
    sample_results = {
        name: run_great(client, path, "hg38")
        for name, path in samples.items()
    }

# Collect top terms across all samples
all_top_terms = set()
for name, df in sample_results.items():
    if df is not None:
        top = df.nsmallest(15, "binom_fdr")["term_name"].tolist()
        all_top_terms.update(top)

top_terms = sorted(all_top_terms)[:30]  # Limit to 30

# Build matrix
matrix = np.zeros((len(top_terms), len(samples)))
sample_names = list(samples.keys())

for j, name in enumerate(sample_names):
    df = sample_results[name]
    if df is not None:
        for i, term in enumerate(top_terms):
            row = df[df["term_name"] == term]
            if not row.empty:
                fdr = row["binom_fdr"].values[0]
                matrix[i, j] = -np.log10(fdr + 1e-300)

# Create heatmap
plt.figure(figsize=(10, 12))
sns.heatmap(
    matrix,
    xticklabels=sample_names,
    yticklabels=top_terms,
    cmap="YlOrRd",
    cbar_kws={"label": "-log10(FDR)"},
)
plt.title("GO Biological Process Enrichment")
plt.tight_layout()
plt.savefig("enrichment_heatmap.png", dpi=300)
```

## Example 4: Custom GenomicRegions

Work with GenomicRegions directly for preprocessing.

```python
import pandas as pd
from pygreat import GreatClient
from pygreat.models import GenomicRegions


# Load and filter regions
regions = GenomicRegions.from_bed("peaks.bed")
df = regions.to_dataframe()

# Filter to specific chromosomes
autosomes = [f"chr{i}" for i in range(1, 23)]
df_filtered = df[df["chrom"].isin(autosomes)]

# Filter by region size
df_filtered = df_filtered[
    (df_filtered["end"] - df_filtered["start"]) >= 100
]

# Create new GenomicRegions
filtered_regions = GenomicRegions.from_dataframe(df_filtered)

print(f"Original: {len(regions)} regions")
print(f"Filtered: {len(filtered_regions)} regions")

# Submit filtered regions
with GreatClient() as client:
    job = client.submit_job(filtered_regions, species="hg38")
    results = job.get_enrichment_tables()
```

## Example 5: Parallel Processing with ThreadPool

Process samples in parallel (create separate clients per thread).

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from pygreat import GreatClient


def process_sample(bed_file, species="hg38"):
    """Process a single sample with its own client."""
    # Each thread needs its own client
    with GreatClient() as client:
        job = client.submit_job(bed_file, species=species)
        results = job.get_enrichment_tables(max_fdr=0.05)

    return bed_file.stem, results


def process_parallel(sample_dir, max_workers=3):
    """Process samples in parallel."""
    sample_dir = Path(sample_dir)
    bed_files = list(sample_dir.glob("*.bed"))

    all_results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_sample, bed): bed
            for bed in bed_files
        }

        for future in as_completed(futures):
            bed_file = futures[future]
            try:
                sample_name, results = future.result()
                all_results[sample_name] = results
                print(f"Completed: {sample_name}")
            except Exception as e:
                print(f"Failed: {bed_file.name} - {e}")

    return all_results


# Process with 3 parallel workers
# Note: Be careful not to exceed GREAT's rate limits
results = process_parallel("samples/", max_workers=3)
```

## Example 6: Custom Visualization

Create a custom volcano-style plot.

```python
import numpy as np
import matplotlib.pyplot as plt
from pygreat import GreatClient


with GreatClient() as client:
    job = client.submit_job("peaks.bed", species="hg38")
    results = job.get_enrichment_tables()

go_bp = results["GO Biological Process"]

# Create volcano-style plot
fig, ax = plt.subplots(figsize=(10, 8))

# Transform data
x = go_bp["binom_fold_enrichment"]
y = -np.log10(go_bp["binom_fdr"])

# Color by significance
colors = np.where(go_bp["binom_fdr"] < 0.05, "red", "gray")

# Size by gene count
sizes = go_bp["observed_genes"] * 3

ax.scatter(x, y, c=colors, s=sizes, alpha=0.6)

# Add labels for top terms
top_terms = go_bp.nsmallest(5, "binom_fdr")
for _, row in top_terms.iterrows():
    ax.annotate(
        row["term_name"][:40],
        (row["binom_fold_enrichment"], -np.log10(row["binom_fdr"])),
        fontsize=8,
        ha="left",
    )

ax.set_xlabel("Fold Enrichment")
ax.set_ylabel("-log10(FDR)")
ax.set_title("GO Biological Process Enrichment")
ax.axhline(-np.log10(0.05), color="red", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig("volcano_plot.png", dpi=300)
```

## Example 7: Export to Excel with Formatting

Create a formatted Excel report.

```python
import pandas as pd
from pygreat import GreatClient


with GreatClient() as client:
    job = client.submit_job("peaks.bed", species="hg38")
    results = job.get_enrichment_tables(max_fdr=0.1)

# Create Excel writer with formatting
with pd.ExcelWriter("report.xlsx", engine="openpyxl") as writer:
    # Write summary sheet
    summary_data = []
    for ont, df in results.items():
        n_sig = (df["binom_fdr"] < 0.05).sum() if not df.empty else 0
        summary_data.append({"Ontology": ont, "Significant Terms": n_sig})

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name="Summary", index=False)

    # Write each ontology
    for ont, df in results.items():
        if not df.empty:
            sheet_name = ont[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Saved report.xlsx")
```

## Example 8: Integration with PyRanges

Convert between pygreat and PyRanges.

```python
import pyranges as pr
from pygreat import GreatClient
from pygreat.models import GenomicRegions


# Load with PyRanges
peaks = pr.read_bed("peaks.bed")

# Filter using PyRanges features
peaks = peaks[peaks.lengths() >= 200]
peaks = peaks.merge()  # Merge overlapping

# Convert to DataFrame for pygreat
df = peaks.df.rename(columns={
    "Chromosome": "chrom",
    "Start": "start",
    "End": "end",
})

# Run GREAT
with GreatClient() as client:
    job = client.submit_job(df, species="hg38")
    results = job.get_enrichment_tables()
```

## Example 9: Caching Results

Cache GREAT results for repeated analysis.

```python
import json
import hashlib
from pathlib import Path
from pygreat import GreatClient


def get_cache_key(bed_file, species, rule):
    """Generate cache key from parameters."""
    content = Path(bed_file).read_bytes()
    h = hashlib.md5(content).hexdigest()
    return f"{species}_{rule}_{h[:8]}"


def run_great_cached(bed_file, species="hg38", rule="basalPlusExt"):
    """Run GREAT with caching."""
    cache_dir = Path(".great_cache")
    cache_dir.mkdir(exist_ok=True)

    cache_key = get_cache_key(bed_file, species, rule)
    cache_file = cache_dir / f"{cache_key}.parquet"

    if cache_file.exists():
        print(f"Loading from cache: {cache_key}")
        return pd.read_parquet(cache_file)

    print(f"Running GREAT analysis...")
    with GreatClient() as client:
        job = client.submit_job(bed_file, species=species, rule=rule)
        df = job.to_dataframe()

    # Cache results
    df.to_parquet(cache_file)
    print(f"Cached: {cache_key}")

    return df


# First run: hits GREAT server
results = run_great_cached("peaks.bed", species="hg38")

# Second run: loads from cache
results = run_great_cached("peaks.bed", species="hg38")
```

## Example 10: Command Line Script

A complete command-line analysis script.

```python
#!/usr/bin/env python3
"""
GREAT enrichment analysis script.

Usage:
    python analyze.py peaks.bed -s hg38 -o results/
"""

import argparse
from pathlib import Path
from pygreat import GreatClient
from pygreat.viz import plot_enrichment_bar, plot_enrichment_dot


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run GREAT enrichment analysis"
    )
    parser.add_argument("bed_file", help="Input BED file")
    parser.add_argument("-s", "--species", default="hg38",
                        choices=["hg38", "hg19", "mm10", "mm9"])
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    parser.add_argument("--max-fdr", type=float, default=0.05)
    parser.add_argument("--min-genes", type=int, default=3)
    parser.add_argument("-n", "--n-terms", type=int, default=15)
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing {args.bed_file}...")

    with GreatClient() as client:
        job = client.submit_job(args.bed_file, species=args.species)
        results = job.get_enrichment_tables(
            max_fdr=args.max_fdr,
            min_genes=args.min_genes,
        )

        # Save all results
        df = job.to_dataframe()
        df.to_csv(output_dir / "all_results.tsv", sep="\t", index=False)

        # Create plots for each ontology
        for ont, ont_df in results.items():
            if ont_df.empty:
                continue

            safe_name = ont.replace(" ", "_").lower()

            # Bar plot
            fig, ax = plot_enrichment_bar(ont_df, n_terms=args.n_terms, title=ont)
            fig.savefig(output_dir / f"{safe_name}_bar.png", dpi=300, bbox_inches="tight")
            plt.close(fig)

            # Dot plot
            fig, ax = plot_enrichment_dot(ont_df, n_terms=args.n_terms, title=ont)
            fig.savefig(output_dir / f"{safe_name}_dot.png", dpi=300, bbox_inches="tight")
            plt.close(fig)

            print(f"  {ont}: {len(ont_df)} terms")

    print(f"\nResults saved to {output_dir}/")


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    main()
```
