# Working with Results

After submitting a job, pygreat returns a `GreatJob` object containing all enrichment results. This guide covers how to access, filter, and export these results.

## Retrieving Enrichment Tables

### Get All Ontologies

```python
from pygreat import GreatClient

client = GreatClient()
job = client.submit_job("peaks.bed", species="hg38")

# Get all enrichment results
results = job.get_enrichment_tables()

# results is a dict: ontology name -> DataFrame
for ontology, df in results.items():
    print(f"{ontology}: {len(df)} terms")
```

### Get Specific Ontologies

```python
# Request specific ontologies
results = job.get_enrichment_tables(
    ontologies=["GO Biological Process", "GO Molecular Function"]
)
```

### Get Single Ontology

```python
# Get one ontology directly
go_bp = job.get_enrichment_table("GO Biological Process")
```

## Available Ontologies

List all available ontologies in the results:

```python
# Flat list
ontologies = job.list_ontologies()
print(ontologies)
# ['GO Biological Process', 'GO Molecular Function', 'GO Cellular Component', ...]

# Grouped by category
categories = job.available_ontologies()
for category, names in categories.items():
    print(f"{category}: {names}")
```

## Filtering Results

### By FDR Threshold

Filter to significant terms:

```python
# During retrieval
results = job.get_enrichment_tables(max_fdr=0.05)

# After retrieval
go_bp = results["GO Biological Process"]
significant = go_bp[go_bp["binom_fdr"] < 0.05]
```

### By Gene Count

Filter by minimum number of observed genes:

```python
# During retrieval
results = job.get_enrichment_tables(min_genes=5)

# After retrieval
go_bp = results["GO Biological Process"]
filtered = go_bp[go_bp["observed_genes"] >= 5]
```

### Combined Filtering

```python
# Both filters
results = job.get_enrichment_tables(
    max_fdr=0.05,
    min_genes=5,
)

# Or chain pandas filters
go_bp = results["GO Biological Process"]
filtered = go_bp[
    (go_bp["binom_fdr"] < 0.05) &
    (go_bp["observed_genes"] >= 5)
]
```

## DataFrame Columns

Each enrichment DataFrame contains these columns:

| Column | Type | Description |
|--------|------|-------------|
| `term_id` | str | Ontology term ID (e.g., GO:0006915) |
| `term_name` | str | Human-readable term name |
| `binom_rank` | int | Binomial test rank |
| `binom_p` | float | Binomial raw p-value |
| `binom_bonferroni` | float | Bonferroni-corrected p-value |
| `binom_fdr` | float | FDR-corrected q-value |
| `binom_fold_enrichment` | float | Fold enrichment (binomial) |
| `observed_regions` | int | Number of input regions for term |
| `expected_regions` | float | Expected regions under null |
| `genome_fraction` | float | Fraction of genome annotated to term |
| `region_coverage` | float | Fraction of input regions annotated |
| `hyper_rank` | int | Hypergeometric test rank |
| `hyper_p` | float | Hypergeometric raw p-value |
| `hyper_bonferroni` | float | Bonferroni-corrected (hyper) |
| `hyper_fdr` | float | FDR-corrected (hyper) |
| `hyper_fold_enrichment` | float | Fold enrichment (hyper) |
| `observed_genes` | int | Number of genes in input regions |
| `expected_genes` | float | Expected genes under null |
| `total_genes` | int | Total genes annotated to term |
| `gene_coverage` | float | Fraction of term genes observed |
| `term_coverage` | float | Fraction of term covered |
| `regions` | str | Comma-separated region names |
| `genes` | str | Comma-separated gene names |

## Sorting Results

```python
go_bp = results["GO Biological Process"]

# Sort by binomial FDR (most significant first)
sorted_df = go_bp.sort_values("binom_fdr")

# Sort by fold enrichment (highest first)
sorted_df = go_bp.sort_values("binom_fold_enrichment", ascending=False)

# Sort by gene count
sorted_df = go_bp.sort_values("observed_genes", ascending=False)
```

## Accessing Metadata

Get information about the job:

```python
# Job metadata
metadata = job.get_metadata()
print(metadata)
# {'version': '4.0.4', 'species': 'hg38', 'rule': 'Basal+extension: ...'}

# Ontology statistics
stats = job.get_ontology_stats()
print(stats["GO Biological Process"])
# {'terms_tested': 13145, 'min_annot_count': '1', 'max_annot_count': 'Inf'}
```

## Exporting Results

### To TSV File

```python
# Export all ontologies (includes 'ontology' column)
df = job.to_dataframe()
df.to_csv("all_results.tsv", sep="\t", index=False)

# Export single ontology
go_bp = job.to_dataframe("GO Biological Process")
go_bp.to_csv("go_bp_results.tsv", sep="\t", index=False)
```

### To Excel

```python
# Export to Excel with multiple sheets
with pd.ExcelWriter("results.xlsx") as writer:
    for ontology, df in results.items():
        # Truncate sheet name to Excel's limit
        sheet_name = ontology[:31]
        df.to_excel(writer, sheet_name=sheet_name, index=False)
```

### To CSV

```python
go_bp = results["GO Biological Process"]
go_bp.to_csv("go_bp.csv", index=False)
```

## Common Analysis Patterns

### Top N Terms

```python
# Top 10 by significance
top10 = go_bp.nsmallest(10, "binom_fdr")

# Top 10 by fold enrichment (among significant)
significant = go_bp[go_bp["binom_fdr"] < 0.05]
top10_enriched = significant.nlargest(10, "binom_fold_enrichment")
```

### Terms with Specific Genes

```python
# Find terms containing a specific gene
gene = "TP53"
terms_with_gene = go_bp[go_bp["genes"].str.contains(gene, na=False)]
```

### Summary Statistics

```python
# Count significant terms per ontology
for ontology, df in results.items():
    n_significant = (df["binom_fdr"] < 0.05).sum()
    print(f"{ontology}: {n_significant} significant terms")
```

### Compare Test Statistics

```python
# Compare binomial and hypergeometric tests
go_bp = results["GO Biological Process"]

# Terms significant in both tests
both_sig = go_bp[
    (go_bp["binom_fdr"] < 0.05) &
    (go_bp["hyper_fdr"] < 0.05)
]

# Correlation between test statistics
correlation = go_bp["binom_fdr"].corr(go_bp["hyper_fdr"])
```
