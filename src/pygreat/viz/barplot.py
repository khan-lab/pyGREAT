"""Bar plot visualizations for enrichment results."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot_enrichment_bar(
    data: pd.DataFrame,
    *,
    n_terms: int = 15,
    value_column: Literal[
        "binom_fdr", "hyper_fdr", "binom_fold_enrichment", "hyper_fold_enrichment"
    ] = "binom_fdr",
    color_column: str | None = None,
    title: str = "Top Enriched Terms",
    xlabel: str | None = None,
    figsize: tuple[float, float] = (10, 8),
    palette: str = "viridis_r",
    ax: Axes | None = None,
) -> tuple[Figure, Axes]:
    """Create a bar plot of top enriched terms.

    Args:
        data: DataFrame with enrichment results.
        n_terms: Number of top terms to display.
        value_column: Column to use for bar values. For FDR columns,
            values are transformed to -log10.
        color_column: Column to use for bar colors (optional).
        title: Plot title.
        xlabel: X-axis label (auto-generated if None).
        figsize: Figure size in inches.
        palette: Seaborn color palette name.
        ax: Existing axes to plot on.

    Returns:
        Tuple of (Figure, Axes).

    Example:
        >>> from pygreat.viz import plot_enrichment_bar
        >>> fig, ax = plot_enrichment_bar(
        ...     results["GO Biological Process"],
        ...     n_terms=20,
        ...     value_column="binom_fdr",
        ... )
        >>> plt.savefig("enrichment.png", dpi=300, bbox_inches="tight")
    """
    if data.empty:
        fig, ax_result = plt.subplots(figsize=figsize)
        ax_result.text(
            0.5, 0.5, "No significant terms", ha="center", va="center", fontsize=12
        )
        ax_result.set_xlim(0, 1)
        ax_result.set_ylim(0, 1)
        ax_result.axis("off")
        return fig, ax_result

    # Sort and select top terms
    is_fdr_or_pval = value_column.endswith("fdr") or value_column.endswith("p")
    if is_fdr_or_pval:
        plot_data = data.nsmallest(n_terms, value_column).copy()
    else:
        plot_data = data.nlargest(n_terms, value_column).copy()

    # Transform values for visualization
    if is_fdr_or_pval:
        # Avoid log(0) by clipping to a small value
        plot_data["plot_value"] = -np.log10(
            plot_data[value_column].clip(lower=1e-300)
        )
        default_xlabel = f"-log10({value_column})"
    else:
        plot_data["plot_value"] = plot_data[value_column]
        default_xlabel = value_column.replace("_", " ").title()

    # Create figure if not provided
    if ax is None:
        fig, ax_result = plt.subplots(figsize=figsize)
    else:
        ax_result = ax
        fig = ax_result.get_figure()  # type: ignore[assignment]

    # Determine colors
    n_bars = len(plot_data)
    if color_column and color_column in plot_data.columns:
        # Color by specified column
        colors = sns.color_palette(palette, n_colors=len(plot_data[color_column].unique()))
        color_map = dict(zip(plot_data[color_column].unique(), colors))
        bar_colors = [color_map[v] for v in plot_data[color_column]]
    else:
        # Color by value (gradient)
        bar_colors = sns.color_palette(palette, n_colors=n_bars)

    # Create horizontal bar plot
    y_positions = range(n_bars)
    ax_result.barh(
        y_positions,
        plot_data["plot_value"],
        color=bar_colors,
        edgecolor="white",
        linewidth=0.5,
    )

    # Set y-axis labels (term names)
    term_labels = plot_data["term_name"].tolist()
    # Truncate long names
    max_label_len = 50
    term_labels = [
        t[:max_label_len] + "..." if len(str(t)) > max_label_len else str(t)
        for t in term_labels
    ]
    ax_result.set_yticks(list(y_positions))
    ax_result.set_yticklabels(term_labels)

    # Styling
    ax_result.set_xlabel(xlabel or default_xlabel)
    ax_result.set_title(title, fontsize=12, fontweight="bold")
    ax_result.invert_yaxis()  # Highest value at top

    # Add gene count annotations if available
    if "observed_genes" in plot_data.columns:
        for i, (_, row) in enumerate(plot_data.iterrows()):
            ax_result.annotate(
                f"n={int(row['observed_genes'])}",
                xy=(row["plot_value"], i),
                xytext=(5, 0),
                textcoords="offset points",
                va="center",
                fontsize=8,
                color="gray",
            )

    sns.despine(ax=ax_result)
    plt.tight_layout()

    return fig, ax_result


def plot_multi_ontology_bar(
    results: dict[str, pd.DataFrame],
    *,
    ontologies: list[str] | None = None,
    n_terms_per_ontology: int = 5,
    figsize: tuple[float, float] = (12, 10),
    palette: str = "Set2",
    title: str = "Top Enriched Terms by Ontology",
) -> tuple[Figure, Axes]:
    """Create a grouped bar plot across multiple ontologies.

    Args:
        results: Dictionary mapping ontology names to DataFrames.
        ontologies: Ontologies to include (None for all).
        n_terms_per_ontology: Terms per ontology.
        figsize: Figure size.
        palette: Color palette name.
        title: Plot title.

    Returns:
        Tuple of (Figure, Axes).

    Example:
        >>> fig, ax = plot_multi_ontology_bar(
        ...     results,
        ...     ontologies=["GO Biological Process", "GO Molecular Function"],
        ...     n_terms_per_ontology=5,
        ... )
    """
    selected = ontologies or list(results.keys())

    # Collect top terms from each ontology
    all_terms = []
    for ontology in selected:
        if ontology not in results:
            continue
        df = results[ontology]
        if df.empty:
            continue
        if "binom_fdr" not in df.columns:
            continue
        top = df.nsmallest(n_terms_per_ontology, "binom_fdr").copy()
        top["ontology"] = ontology
        all_terms.append(top)

    if not all_terms:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No significant terms", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig, ax

    combined = pd.concat(all_terms, ignore_index=True)
    combined["neg_log_fdr"] = -np.log10(combined["binom_fdr"].clip(lower=1e-300))

    # Truncate long term names
    max_label_len = 40
    combined["term_label"] = combined["term_name"].apply(
        lambda t: str(t)[:max_label_len] + "..." if len(str(t)) > max_label_len else str(t)
    )

    fig, ax = plt.subplots(figsize=figsize)

    sns.barplot(
        data=combined,
        y="term_label",
        x="neg_log_fdr",
        hue="ontology",
        ax=ax,
        palette=palette,
    )

    ax.set_xlabel("-log10(FDR)")
    ax.set_ylabel("")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.legend(title="Ontology", bbox_to_anchor=(1.02, 1), loc="upper left")

    sns.despine(ax=ax)
    plt.tight_layout()

    return fig, ax
