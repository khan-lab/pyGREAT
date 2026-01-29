"""Tests for EnrichmentResult model."""

import pandas as pd
import pytest

from pygreat.models.enrichment import EnrichmentResult


class TestEnrichmentResult:
    """Tests for EnrichmentResult class."""

    @pytest.fixture
    def enrichment_result(self, sample_enrichment_df: pd.DataFrame) -> EnrichmentResult:
        """Create sample enrichment result."""
        return EnrichmentResult(
            results={
                "GO Biological Process": sample_enrichment_df.copy(),
                "GO Molecular Function": sample_enrichment_df.copy(),
            },
            job_id="test_session",
            species="hg38",
            rule="basalPlusExt",
        )

    def test_len(self, enrichment_result: EnrichmentResult) -> None:
        """Test length calculation."""
        # 3 terms * 2 ontologies = 6
        assert len(enrichment_result) == 6

    def test_contains(self, enrichment_result: EnrichmentResult) -> None:
        """Test ontology membership check."""
        assert "GO Biological Process" in enrichment_result
        assert "Unknown Ontology" not in enrichment_result

    def test_getitem(self, enrichment_result: EnrichmentResult) -> None:
        """Test dictionary-style access."""
        df = enrichment_result["GO Biological Process"]
        assert len(df) == 3

    def test_ontologies(self, enrichment_result: EnrichmentResult) -> None:
        """Test listing ontologies."""
        ontologies = enrichment_result.ontologies()
        assert "GO Biological Process" in ontologies
        assert "GO Molecular Function" in ontologies

    def test_get_top_terms_single_ontology(
        self, enrichment_result: EnrichmentResult
    ) -> None:
        """Test getting top terms from single ontology."""
        top = enrichment_result.get_top_terms(
            ontology="GO Biological Process", n=2, sort_by="binom_fdr"
        )
        assert len(top) == 2
        assert top.iloc[0]["term_id"] == "GO:0006915"  # Lowest FDR

    def test_get_top_terms_all_ontologies(
        self, enrichment_result: EnrichmentResult
    ) -> None:
        """Test getting top terms across all ontologies."""
        top = enrichment_result.get_top_terms(n=4, sort_by="binom_fdr")
        assert len(top) == 4
        assert "ontology" in top.columns

    def test_get_top_terms_fold_enrichment(
        self, enrichment_result: EnrichmentResult
    ) -> None:
        """Test sorting by fold enrichment."""
        top = enrichment_result.get_top_terms(
            ontology="GO Biological Process",
            n=2,
            sort_by="binom_fold_enrichment",
            ascending=False,
        )
        assert top.iloc[0]["term_id"] == "GO:0006915"  # Highest fold enrichment

    def test_filter_by_fdr(self, enrichment_result: EnrichmentResult) -> None:
        """Test filtering by FDR."""
        filtered = enrichment_result.filter(max_fdr=0.001)
        # Only GO:0006915 has FDR < 0.001
        for df in filtered.results.values():
            assert all(df["binom_fdr"] <= 0.001)

    def test_filter_by_min_genes(self, enrichment_result: EnrichmentResult) -> None:
        """Test filtering by minimum genes."""
        filtered = enrichment_result.filter(min_genes=15, max_fdr=1.0)
        for df in filtered.results.values():
            assert all(df["observed_genes"] >= 15)

    def test_filter_by_fold_enrichment(
        self, enrichment_result: EnrichmentResult
    ) -> None:
        """Test filtering by fold enrichment."""
        filtered = enrichment_result.filter(
            min_fold_enrichment=2.0, max_fdr=1.0, test="binom"
        )
        for df in filtered.results.values():
            assert all(df["binom_fold_enrichment"] >= 2.0)

    def test_to_dataframe(self, enrichment_result: EnrichmentResult) -> None:
        """Test combining to single DataFrame."""
        df = enrichment_result.to_dataframe()
        assert len(df) == 6  # 3 terms * 2 ontologies
        assert "ontology" in df.columns

    def test_to_dataframe_no_ontology_column(
        self, enrichment_result: EnrichmentResult
    ) -> None:
        """Test DataFrame without ontology column."""
        df = enrichment_result.to_dataframe(include_ontology=False)
        assert "ontology" not in df.columns

    def test_summary(self, enrichment_result: EnrichmentResult) -> None:
        """Test summary statistics."""
        summary = enrichment_result.summary()
        assert len(summary) == 2
        assert "total_terms" in summary.columns
        assert "significant_terms" in summary.columns
        assert summary.iloc[0]["total_terms"] == 3
