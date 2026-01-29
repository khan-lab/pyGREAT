# GreatJob

::: pygreat.core.job.GreatJob
    options:
      show_source: false

## Overview

`GreatJob` represents a completed GREAT analysis job. It contains all enrichment results retrieved from the GREAT batch API and provides methods to access, filter, and export these results.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `job_id` | `str` | Job identifier (typically the hosted file URL) |
| `species` | `str` | Genome assembly used |
| `rule` | `str` | Association rule used |
| `job_name` | `str \| None` | User-provided job name |
| `enrichment_results` | `dict[str, DataFrame]` | Results by ontology |
| `metadata` | `dict[str, str]` | Job metadata from GREAT |
| `ontology_stats` | `dict` | Summary statistics per ontology |

## Methods

### get_enrichment_tables

Retrieve enrichment results for multiple ontologies.

```python
def get_enrichment_tables(
    self,
    ontologies: list[str] | None = None,
    *,
    min_genes: int = 1,
    max_fdr: float = 1.0,
) -> dict[str, pd.DataFrame]
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ontologies` | `list[str] \| None` | `None` | Ontologies to retrieve. None = all available |
| `min_genes` | `int` | `1` | Minimum observed genes per term |
| `max_fdr` | `float` | `1.0` | Maximum FDR threshold |

#### Returns

`dict[str, DataFrame]` - Dictionary mapping ontology names to result DataFrames.

#### Example

```python
# All ontologies
results = job.get_enrichment_tables()

# Specific ontologies
results = job.get_enrichment_tables(
    ontologies=["GO Biological Process", "GO Molecular Function"]
)

# With filtering
results = job.get_enrichment_tables(max_fdr=0.05, min_genes=5)
```

### get_enrichment_table

Retrieve enrichment results for a single ontology.

```python
def get_enrichment_table(
    self,
    ontology: str,
    *,
    min_genes: int = 1,
    max_fdr: float = 1.0,
) -> pd.DataFrame
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ontology` | `str` | Required | Ontology name |
| `min_genes` | `int` | `1` | Minimum observed genes |
| `max_fdr` | `float` | `1.0` | Maximum FDR threshold |

#### Returns

`DataFrame` - Enrichment results for the specified ontology.

#### Example

```python
go_bp = job.get_enrichment_table("GO Biological Process")
significant = job.get_enrichment_table("GO Biological Process", max_fdr=0.05)
```

### list_ontologies

Get a flat list of all available ontology names.

```python
def list_ontologies(self) -> list[str]
```

#### Returns

`list[str]` - List of ontology names.

#### Example

```python
ontologies = job.list_ontologies()
# ['GO Biological Process', 'GO Molecular Function', 'GO Cellular Component', ...]
```

### available_ontologies

Get ontologies grouped by category.

```python
def available_ontologies(self) -> dict[str, list[str]]
```

#### Returns

`dict[str, list[str]]` - Dictionary mapping category names to ontology lists.

#### Example

```python
categories = job.available_ontologies()
# {'Gene Ontology': ['GO Biological Process', ...], 'Pathway Data': [...]}
```

### get_metadata

Get job metadata from GREAT response.

```python
def get_metadata(self) -> dict[str, str]
```

#### Returns

`dict[str, str]` - Dictionary with version, species, and rule information.

#### Example

```python
meta = job.get_metadata()
print(meta)
# {'version': '4.0.4', 'species': 'hg38', 'rule': 'Basal+extension: ...'}
```

### get_ontology_stats

Get ontology summary statistics.

```python
def get_ontology_stats(self) -> dict[str, dict[str, Any]]
```

#### Returns

`dict[str, dict]` - Dictionary mapping ontology names to their statistics.

#### Example

```python
stats = job.get_ontology_stats()
print(stats["GO Biological Process"])
# {'terms_tested': 13145, 'min_annot_count': '1', 'max_annot_count': 'Inf'}
```

### to_dataframe

Export results as a single DataFrame.

```python
def to_dataframe(self, ontology: str | None = None) -> pd.DataFrame
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `ontology` | `str \| None` | `None` | Specific ontology to export. None = all ontologies |

#### Returns

`DataFrame` - Enrichment results. When exporting all ontologies, includes an 'ontology' column.

#### Example

```python
# Export all ontologies
df = job.to_dataframe()
df.to_csv("all_results.tsv", sep="\t", index=False)

# Export single ontology
go_bp = job.to_dataframe("GO Biological Process")
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
| `binom_fold_enrichment` | float | Binomial fold enrichment |
| `observed_regions` | int | Input regions annotated to term |
| `expected_regions` | float | Expected regions under null |
| `genome_fraction` | float | Fraction of genome annotated to term |
| `region_coverage` | float | Fraction of input regions |
| `hyper_rank` | int | Hypergeometric test rank |
| `hyper_p` | float | Hypergeometric raw p-value |
| `hyper_bonferroni` | float | Hypergeometric Bonferroni |
| `hyper_fdr` | float | Hypergeometric FDR |
| `hyper_fold_enrichment` | float | Hypergeometric fold enrichment |
| `observed_genes` | int | Genes in input regions |
| `expected_genes` | float | Expected genes under null |
| `total_genes` | int | Total genes annotated to term |
| `gene_coverage` | float | Fraction of term genes observed |
| `term_coverage` | float | Term coverage |
| `regions` | str | Comma-separated region names |
| `genes` | str | Comma-separated gene names |

## Example Workflow

```python
from pygreat import GreatClient

# Submit job
client = GreatClient()
job = client.submit_job("peaks.bed", species="hg38")

# Check available ontologies
print(job.list_ontologies())

# Get filtered results
results = job.get_enrichment_tables(max_fdr=0.05, min_genes=5)

# Access GO Biological Process
go_bp = results["GO Biological Process"]
print(f"Found {len(go_bp)} significant terms")

# Sort by significance
top_terms = go_bp.nsmallest(10, "binom_fdr")
print(top_terms[["term_name", "binom_fdr", "observed_genes"]])

# Export to file
df = job.to_dataframe()
df.to_csv("results.tsv", sep="\t", index=False)

# Clean up
client.close()
```
