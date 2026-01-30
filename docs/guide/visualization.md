# Visualization

pygreat provides publication-ready visualizations for enrichment results using seaborn and matplotlib, as well as interactive HTML reports.

## Interactive HTML Reports

Generate a self-contained interactive HTML report from your enrichment results. The report includes everything you need to explore and present your results without writing any code.

### Features

- **Summary Panel** - Overview of total terms and significant terms per ontology
- **Interactive Tables** - Search, sort, and paginate through results with DataTables
- **Global Filters** - Filter by FDR threshold, p-value, category, and top N terms
- **Term Details** - Click any term to see full statistics, gene list, and links to AmiGO/QuickGO
- **Plot Builder** - Create bar or dot plots from selected terms directly in the browser
- **Export** - Download plots as SVG/PNG and data as TSV/CSV

### CLI Usage

```bash
# Generate HTML report from enrichment results
pygreat report results.tsv -o report.html

# Custom title
pygreat report results.tsv -o report.html -t "ChIP-seq Enrichment Analysis"

# Stricter default FDR threshold
pygreat report results.tsv -o report.html --fdr-threshold 0.01
```

### Python Usage

```python
from pygreat.report import ReportGenerator, ReportConfig

# Basic usage
generator = ReportGenerator()
generator.generate("results.tsv", "report.html")

# With custom configuration
config = ReportConfig(
    title="My Enrichment Analysis",
    default_fdr=0.01,
    default_top_n=50,
)
generator = ReportGenerator(config)
generator.generate("results.tsv", "report.html")

# Generate from DataFrame
import pandas as pd
df = pd.read_csv("results.tsv", sep="\t")
generator.generate(df, "report.html")
```

### Report Walkthrough

1. **Summary Cards** - At the top, see total terms and significant terms (FDR < 0.05) for each ontology category
2. **Filter Bar** - Use the search box, FDR/p-value dropdowns, and Top N selector to focus on terms of interest
3. **Ontology Accordion** - Click to expand/collapse each ontology section (Biological Process, Molecular Function, etc.)
4. **Data Tables** - Each table is sortable and searchable; click column headers to sort
5. **Row Selection** - Check boxes to select terms for plotting
6. **Term Modal** - Click a term name to see detailed statistics and copy the gene list
7. **Plot Builder** - Select terms, choose plot type (bar/dot), customize settings, and generate interactive Plotly plots
8. **Export** - Download your customized plots or filtered data

---

## Bar Plot

The bar plot shows the top enriched terms with -log10(FDR) values:

```python
from pygreat import GreatClient
from pygreat.viz import plot_enrichment_bar

# Get results
client = GreatClient()
job = client.submit_job("peaks.bed", species="hg38")
results = job.get_enrichment_tables()

# Get significant GO terms
go_bp = results["GO Biological Process"]
significant = go_bp[go_bp["binom_fdr"] < 0.05]

# Create bar plot
fig, ax = plot_enrichment_bar(significant, n_terms=15)
fig.savefig("barplot.png", dpi=300, bbox_inches="tight")
```

### Customization Options

```python
fig, ax = plot_enrichment_bar(
    df,
    n_terms=20,                    # Number of terms to show
    pvalue_col="binom_fdr",        # Column for significance
    name_col="term_name",          # Column for term names
    title="GO Biological Process", # Plot title
    xlabel="-log10(FDR)",          # X-axis label
    color="steelblue",             # Bar color
    figsize=(10, 8),               # Figure size
    max_label_length=50,           # Truncate long labels
)
```

### Color by Enrichment

```python
import matplotlib.pyplot as plt

fig, ax = plot_enrichment_bar(
    significant,
    n_terms=15,
    color=significant["binom_fold_enrichment"],  # Color by fold enrichment
)
plt.colorbar(ax.collections[0], label="Fold Enrichment")
```

## Dot Plot

The dot plot shows significance (x-axis), gene count (dot size), and fold enrichment (color):

```python
from pygreat.viz import plot_enrichment_dot

fig, ax = plot_enrichment_dot(significant, n_terms=15)
fig.savefig("dotplot.png", dpi=300, bbox_inches="tight")
```

### Customization Options

```python
fig, ax = plot_enrichment_dot(
    df,
    n_terms=20,                     # Number of terms
    pvalue_col="binom_fdr",         # Significance column
    size_col="observed_genes",      # Column for dot size
    color_col="binom_fold_enrichment",  # Column for color
    name_col="term_name",           # Term name column
    title="GO Enrichment",          # Plot title
    xlabel="-log10(FDR)",           # X-axis label
    figsize=(10, 8),                # Figure size
    cmap="viridis",                 # Colormap
    size_range=(50, 500),           # Min/max dot sizes
    max_label_length=50,            # Truncate labels
)
```

## Saving Figures

### Different Formats

```python
# PNG (raster, good for web)
fig.savefig("plot.png", dpi=300, bbox_inches="tight")

# PDF (vector, good for publications)
fig.savefig("plot.pdf", bbox_inches="tight")

# SVG (vector, good for editing)
fig.savefig("plot.svg", bbox_inches="tight")
```

### Transparent Background

```python
fig.savefig("plot.png", dpi=300, bbox_inches="tight", transparent=True)
```

## Multiple Ontologies

Create plots for multiple ontologies:

```python
import matplotlib.pyplot as plt
from pygreat.viz import plot_enrichment_bar

ontologies = ["GO Biological Process", "GO Molecular Function", "GO Cellular Component"]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, ontology in zip(axes, ontologies):
    df = results.get(ontology)
    if df is not None and not df.empty:
        significant = df[df["binom_fdr"] < 0.05]
        if not significant.empty:
            plot_enrichment_bar(significant, n_terms=10, ax=ax, title=ontology)

plt.tight_layout()
fig.savefig("all_ontologies.png", dpi=300, bbox_inches="tight")
```

## Comparison Plot

Compare enrichment across conditions:

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Assume you have results from two conditions
# condition1_results and condition2_results

# Merge top terms
top_terms = set(
    condition1["GO Biological Process"].nsmallest(20, "binom_fdr")["term_name"]
) | set(
    condition2["GO Biological Process"].nsmallest(20, "binom_fdr")["term_name"]
)

# Create comparison DataFrame
comparison = []
for term in top_terms:
    for cond, results in [("Condition 1", condition1), ("Condition 2", condition2)]:
        df = results["GO Biological Process"]
        row = df[df["term_name"] == term]
        if not row.empty:
            comparison.append({
                "term": term,
                "condition": cond,
                "neg_log_fdr": -np.log10(row["binom_fdr"].values[0]),
            })

comp_df = pd.DataFrame(comparison)

# Create grouped bar plot
plt.figure(figsize=(12, 8))
sns.barplot(data=comp_df, y="term", x="neg_log_fdr", hue="condition")
plt.xlabel("-log10(FDR)")
plt.ylabel("")
plt.title("GO Enrichment Comparison")
plt.tight_layout()
plt.savefig("comparison.png", dpi=300)
```

## Heatmap

Create a heatmap of enrichment across multiple samples:

```python
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Collect -log10(FDR) for top terms across samples
samples = ["Sample1", "Sample2", "Sample3"]
top_terms = ["apoptotic process", "cell cycle", "DNA repair", ...]  # Your terms

# Build matrix
matrix = np.zeros((len(top_terms), len(samples)))
for j, sample in enumerate(samples):
    df = sample_results[sample]["GO Biological Process"]
    for i, term in enumerate(top_terms):
        row = df[df["term_name"] == term]
        if not row.empty:
            matrix[i, j] = -np.log10(row["binom_fdr"].values[0])

# Create heatmap
plt.figure(figsize=(8, 10))
sns.heatmap(
    matrix,
    xticklabels=samples,
    yticklabels=top_terms,
    cmap="YlOrRd",
    cbar_kws={"label": "-log10(FDR)"},
)
plt.title("GO Enrichment Heatmap")
plt.tight_layout()
plt.savefig("heatmap.png", dpi=300)
```

## CLI Visualization

Create plots from the command line:

```bash
# Bar plot (default)
pygreat plot results.tsv -t "GO Biological Process" -o barplot.png

# Dot plot
pygreat plot results.tsv -t "GO Biological Process" --plot-type dot -o dotplot.png

# Customize number of terms
pygreat plot results.tsv -t "GO Biological Process" -n 20 -o barplot.png
```

## Styling Tips

### Publication Quality

```python
import matplotlib.pyplot as plt

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
})

fig, ax = plot_enrichment_bar(significant, n_terms=15)
fig.savefig("publication_plot.pdf", bbox_inches="tight")
```

### Dark Theme

```python
plt.style.use('dark_background')
fig, ax = plot_enrichment_bar(significant, n_terms=15, color="lightblue")
```
