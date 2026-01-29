"""Dot plot visualizations for enrichment results."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot_enrichment_dot(
    data: pd.DataFrame,
    *,
    n_terms: int = 20,
    size_column: str = "observed_genes",
    color_column: str = "binom_fdr",
    x_column: str = "binom_fold_enrichment",
    title: str = "Enrichment Dot Plot",
    figsize: tuple[float, float] = (10, 8),
    cmap: str = "RdYlBu_r",
    size_range: tuple[int, int] = (50, 400),
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Create a dot plot of enrichment results.

    Dot size represents gene count, color represents significance,
    and x-position represents fold enrichment.

    Args:
        data: DataFrame with enrichment results.
        n_terms: Number of terms to display.
        size_column: Column for dot size (typically gene count).
        color_column: Column for dot color (typically FDR).
        x_column: Column for x-axis values (typically fold enrichment).
        title: Plot title.
        figsize: Figure size in inches.
        cmap: Matplotlib colormap for significance.
        size_range: Min and max dot sizes in points.
        ax: Existing axes to plot on.

    Returns:
        Tuple of (Figure, Axes).

    Example:
        >>> from pygreat.viz import plot_enrichment_dot
        >>> fig, ax = plot_enrichment_dot(
        ...     results["GO Biological Process"],
        ...     n_terms=25,
        ...     size_column="observed_genes",
        ...     color_column="binom_fdr",
        ... )
        >>> plt.savefig("dotplot.png", dpi=300, bbox_inches="tight")
    """
    if data.empty:
        fig, ax_result = plt.subplots(figsize=figsize)
        ax_result.text(
            0.5, 0.5, "No significant terms", ha="center", va="center", fontsize=12
        )
        ax_result.axis("off")
        return fig, ax_result

    # Check required columns
    required_cols = [size_column, color_column, x_column, "term_name"]
    missing = [c for c in required_cols if c not in data.columns]
    if missing:
        fig, ax_result = plt.subplots(figsize=figsize)
        ax_result.text(
            0.5, 0.5, f"Missing columns: {missing}", ha="center", va="center"
        )
        ax_result.axis("off")
        return fig, ax_result

    # Select top terms by FDR
    if "binom_fdr" in data.columns:
        plot_data = data.nsmallest(n_terms, "binom_fdr").copy()
    else:
        plot_data = data.head(n_terms).copy()

    # Transform FDR to -log10 for coloring
    is_fdr = color_column.endswith("fdr") or color_column.endswith("p")
    if is_fdr:
        plot_data["color_value"] = -np.log10(
            plot_data[color_column].clip(lower=1e-300)
        )
        color_label = f"-log10({color_column})"
    else:
        plot_data["color_value"] = plot_data[color_column]
        color_label = color_column.replace("_", " ").title()

    # Normalize sizes
    sizes = plot_data[size_column].astype(float)
    if sizes.max() > sizes.min():
        size_norm = (sizes - sizes.min()) / (sizes.max() - sizes.min())
    else:
        size_norm = pd.Series([0.5] * len(sizes))
    plot_data["size_scaled"] = size_range[0] + size_norm * (size_range[1] - size_range[0])

    if ax is None:
        fig, ax_result = plt.subplots(figsize=figsize)
    else:
        ax_result = ax
        fig = ax_result.get_figure()  # type: ignore[assignment]

    # Create scatter plot
    scatter = ax_result.scatter(
        plot_data[x_column],
        range(len(plot_data)),
        s=plot_data["size_scaled"],
        c=plot_data["color_value"],
        cmap=cmap,
        alpha=0.8,
        edgecolors="black",
        linewidths=0.5,
    )

    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax_result, shrink=0.7, pad=0.02)
    cbar.set_label(color_label)

    # Y-axis labels
    term_labels = plot_data["term_name"].tolist()
    max_len = 45
    term_labels = [
        str(t)[:max_len] + "..." if len(str(t)) > max_len else str(t)
        for t in term_labels
    ]
    ax_result.set_yticks(range(len(plot_data)))
    ax_result.set_yticklabels(term_labels)

    ax_result.set_xlabel(x_column.replace("_", " ").title())
    ax_result.set_title(title, fontsize=12, fontweight="bold")
    ax_result.invert_yaxis()

    # Size legend
    sizes_for_legend = plot_data[size_column]
    size_values = [sizes_for_legend.min(), sizes_for_legend.median(), sizes_for_legend.max()]
    size_scaled_values = [size_range[0], (size_range[0] + size_range[1]) / 2, size_range[1]]

    handles = [
        plt.scatter(
            [], [],
            s=s,
            c="gray",
            alpha=0.6,
            edgecolors="black",
            linewidths=0.5,
        )
        for s in size_scaled_values
    ]
    labels = [f"{int(s)}" for s in size_values]
    ax_result.legend(
        handles,
        labels,
        title=size_column.replace("_", " ").title(),
        loc="lower right",
        frameon=True,
        labelspacing=1.5,
    )

    sns.despine(ax=ax_result)
    plt.tight_layout()

    return fig, ax_result
