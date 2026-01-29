"""Tests for visualization functions."""

import pandas as pd
import pytest

from pygreat.viz.barplot import plot_enrichment_bar, plot_multi_ontology_bar
from pygreat.viz.dotplot import plot_enrichment_dot


class TestBarPlot:
    """Tests for bar plot functions."""

    def test_plot_enrichment_bar(self, sample_enrichment_df: pd.DataFrame) -> None:
        """Test basic bar plot creation."""
        fig, ax = plot_enrichment_bar(sample_enrichment_df, n_terms=3)
        assert fig is not None
        assert ax is not None
        # Check y-axis labels
        assert len(ax.get_yticklabels()) == 3

    def test_plot_enrichment_bar_empty(self) -> None:
        """Test bar plot with empty data."""
        fig, ax = plot_enrichment_bar(pd.DataFrame())
        assert fig is not None
        # Should show "No significant terms" message

    def test_plot_enrichment_bar_fold_enrichment(
        self, sample_enrichment_df: pd.DataFrame
    ) -> None:
        """Test bar plot with fold enrichment."""
        fig, ax = plot_enrichment_bar(
            sample_enrichment_df,
            value_column="binom_fold_enrichment",
            n_terms=3,
        )
        assert fig is not None

    def test_plot_multi_ontology_bar(
        self, sample_enrichment_df: pd.DataFrame
    ) -> None:
        """Test multi-ontology bar plot."""
        results = {
            "GO Biological Process": sample_enrichment_df,
            "GO Molecular Function": sample_enrichment_df,
        }
        fig, ax = plot_multi_ontology_bar(results, n_terms_per_ontology=2)
        assert fig is not None
        assert ax is not None

    def test_plot_multi_ontology_bar_empty(self) -> None:
        """Test multi-ontology plot with empty results."""
        results = {"Empty": pd.DataFrame()}
        fig, ax = plot_multi_ontology_bar(results)
        assert fig is not None


class TestDotPlot:
    """Tests for dot plot functions."""

    def test_plot_enrichment_dot(self, sample_enrichment_df: pd.DataFrame) -> None:
        """Test basic dot plot creation."""
        fig, ax = plot_enrichment_dot(sample_enrichment_df, n_terms=3)
        assert fig is not None
        assert ax is not None

    def test_plot_enrichment_dot_empty(self) -> None:
        """Test dot plot with empty data."""
        fig, ax = plot_enrichment_dot(pd.DataFrame())
        assert fig is not None

    def test_plot_enrichment_dot_custom_columns(
        self, sample_enrichment_df: pd.DataFrame
    ) -> None:
        """Test dot plot with custom column mappings."""
        fig, ax = plot_enrichment_dot(
            sample_enrichment_df,
            size_column="total_genes",
            color_column="hyper_fdr",
            x_column="hyper_fold_enrichment",
            n_terms=3,
        )
        assert fig is not None

    def test_plot_enrichment_dot_missing_columns(self) -> None:
        """Test dot plot with missing required columns."""
        df = pd.DataFrame({"foo": [1, 2, 3]})
        fig, ax = plot_enrichment_dot(df)
        # Should handle gracefully
        assert fig is not None
