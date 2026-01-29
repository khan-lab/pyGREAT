# Visualization

::: pygreat.viz
    options:
      show_source: false

## Overview

pygreat provides two visualization functions for creating publication-ready enrichment plots:

- `plot_enrichment_bar` - Horizontal bar plot of top enriched terms
- `plot_enrichment_dot` - Dot plot showing significance, gene count, and fold enrichment

Both functions use seaborn and matplotlib and return a figure and axes object for further customization.

## plot_enrichment_bar

Create a horizontal bar plot showing -log10(FDR) for top enriched terms.

```python
from pygreat.viz import plot_enrichment_bar
```

### Signature

```python
def plot_enrichment_bar(
    df: pd.DataFrame,
    n_terms: int = 15,
    pvalue_col: str = "binom_fdr",
    name_col: str = "term_name",
    title: str | None = None,
    xlabel: str = "-log10(FDR)",
    color: str | Sequence = "steelblue",
    figsize: tuple[float, float] = (10, 8),
    ax: plt.Axes | None = None,
    max_label_length: int = 50,
) -> tuple[plt.Figure, plt.Axes]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `DataFrame` | Required | Enrichment results DataFrame |
| `n_terms` | `int` | `15` | Number of top terms to show |
| `pvalue_col` | `str` | `"binom_fdr"` | Column name for p-values/FDR |
| `name_col` | `str` | `"term_name"` | Column name for term names |
| `title` | `str \| None` | `None` | Plot title |
| `xlabel` | `str` | `"-log10(FDR)"` | X-axis label |
| `color` | `str \| Sequence` | `"steelblue"` | Bar color(s) |
| `figsize` | `tuple` | `(10, 8)` | Figure size (width, height) |
| `ax` | `Axes \| None` | `None` | Existing axes to plot on |
| `max_label_length` | `int` | `50` | Truncate labels longer than this |

### Returns

`tuple[Figure, Axes]` - Matplotlib figure and axes objects.

### Examples

```python
from pygreat.viz import plot_enrichment_bar

# Basic usage
fig, ax = plot_enrichment_bar(go_bp, n_terms=15)
fig.savefig("barplot.png", dpi=300, bbox_inches="tight")

# With title
fig, ax = plot_enrichment_bar(
    go_bp,
    n_terms=20,
    title="GO Biological Process Enrichment",
)

# Custom color
fig, ax = plot_enrichment_bar(go_bp, color="darkred")

# Color by fold enrichment
fig, ax = plot_enrichment_bar(
    go_bp,
    color=go_bp["binom_fold_enrichment"],
)
```

## plot_enrichment_dot

Create a dot plot showing significance (x-axis), gene count (dot size), and fold enrichment (color).

```python
from pygreat.viz import plot_enrichment_dot
```

### Signature

```python
def plot_enrichment_dot(
    df: pd.DataFrame,
    n_terms: int = 15,
    pvalue_col: str = "binom_fdr",
    size_col: str = "observed_genes",
    color_col: str = "binom_fold_enrichment",
    name_col: str = "term_name",
    title: str | None = None,
    xlabel: str = "-log10(FDR)",
    figsize: tuple[float, float] = (10, 8),
    ax: plt.Axes | None = None,
    cmap: str = "viridis",
    size_range: tuple[float, float] = (50, 500),
    max_label_length: int = 50,
) -> tuple[plt.Figure, plt.Axes]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `DataFrame` | Required | Enrichment results DataFrame |
| `n_terms` | `int` | `15` | Number of top terms to show |
| `pvalue_col` | `str` | `"binom_fdr"` | Column for p-values/FDR |
| `size_col` | `str` | `"observed_genes"` | Column for dot sizes |
| `color_col` | `str` | `"binom_fold_enrichment"` | Column for dot colors |
| `name_col` | `str` | `"term_name"` | Column for term names |
| `title` | `str \| None` | `None` | Plot title |
| `xlabel` | `str` | `"-log10(FDR)"` | X-axis label |
| `figsize` | `tuple` | `(10, 8)` | Figure size |
| `ax` | `Axes \| None` | `None` | Existing axes to plot on |
| `cmap` | `str` | `"viridis"` | Matplotlib colormap name |
| `size_range` | `tuple` | `(50, 500)` | Min and max dot sizes |
| `max_label_length` | `int` | `50` | Truncate labels longer than this |

### Returns

`tuple[Figure, Axes]` - Matplotlib figure and axes objects.

### Examples

```python
from pygreat.viz import plot_enrichment_dot

# Basic usage
fig, ax = plot_enrichment_dot(go_bp, n_terms=15)
fig.savefig("dotplot.png", dpi=300, bbox_inches="tight")

# Custom colormap
fig, ax = plot_enrichment_dot(
    go_bp,
    n_terms=20,
    cmap="YlOrRd",
)

# Custom size range
fig, ax = plot_enrichment_dot(
    go_bp,
    size_range=(20, 300),
)
```

## Common Patterns

### Save in Multiple Formats

```python
fig, ax = plot_enrichment_bar(go_bp)

# Raster formats
fig.savefig("plot.png", dpi=300, bbox_inches="tight")
fig.savefig("plot.jpg", dpi=300, bbox_inches="tight")

# Vector formats (for publications)
fig.savefig("plot.pdf", bbox_inches="tight")
fig.savefig("plot.svg", bbox_inches="tight")
```

### Subplots

```python
import matplotlib.pyplot as plt
from pygreat.viz import plot_enrichment_bar

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Bar plot
plot_enrichment_bar(go_bp, ax=axes[0], title="GO Biological Process")

# Another ontology
plot_enrichment_bar(go_mf, ax=axes[1], title="GO Molecular Function")

plt.tight_layout()
fig.savefig("comparison.png", dpi=300, bbox_inches="tight")
```

### Publication Style

```python
import matplotlib.pyplot as plt

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12,
    'font.family': 'sans-serif',
    'axes.labelsize': 14,
    'axes.titlesize': 16,
})

fig, ax = plot_enrichment_bar(go_bp, n_terms=15)
fig.savefig("publication_figure.pdf", bbox_inches="tight")
```

### Add Significance Line

```python
fig, ax = plot_enrichment_bar(go_bp)

# Add line at FDR = 0.05
ax.axvline(-np.log10(0.05), color='red', linestyle='--', label='FDR = 0.05')
ax.legend()

fig.savefig("with_threshold.png", dpi=300, bbox_inches="tight")
```
