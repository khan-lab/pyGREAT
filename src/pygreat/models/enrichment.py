"""Enrichment result data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import pandas as pd


@dataclass
class EnrichmentTerm:
    """Single enrichment term result.

    Attributes:
        term_id: Ontology term identifier (e.g., 'GO:0006915').
        term_name: Human-readable term name.
        ontology: Ontology name (e.g., 'GO Biological Process').
        binom_p: Binomial raw p-value.
        binom_fdr: Binomial FDR-corrected p-value.
        binom_fold_enrichment: Binomial fold enrichment.
        hyper_p: Hypergeometric raw p-value.
        hyper_fdr: Hypergeometric FDR-corrected p-value.
        hyper_fold_enrichment: Hypergeometric fold enrichment.
        observed_genes: Number of observed genes.
        total_genes: Total genes in term.
        observed_regions: Number of observed regions.
        gene_coverage: Fraction of term genes observed.
        region_coverage: Fraction of regions associated with term.
    """

    term_id: str
    term_name: str
    ontology: str
    binom_p: float
    binom_fdr: float
    binom_fold_enrichment: float
    hyper_p: float
    hyper_fdr: float
    hyper_fold_enrichment: float
    observed_genes: int
    total_genes: int
    observed_regions: int
    gene_coverage: float
    region_coverage: float


@dataclass
class EnrichmentResult:
    """Collection of enrichment results across ontologies.

    Provides convenient access and filtering methods.

    Attributes:
        results: Dictionary mapping ontology names to result DataFrames.
        job_id: GREAT session ID.
        species: Genome assembly used.
        rule: Association rule used.
    """

    results: dict[str, pd.DataFrame] = field(default_factory=dict)
    job_id: str = ""
    species: str = ""
    rule: str = ""

    def __len__(self) -> int:
        """Return total number of terms across all ontologies."""
        return sum(len(df) for df in self.results.values())

    def __contains__(self, ontology: str) -> bool:
        """Check if ontology is present."""
        return ontology in self.results

    def __getitem__(self, ontology: str) -> pd.DataFrame:
        """Get results for a specific ontology."""
        return self.results[ontology]

    def ontologies(self) -> list[str]:
        """Return list of available ontology names."""
        return list(self.results.keys())

    def get_top_terms(
        self,
        ontology: str | None = None,
        n: int = 10,
        sort_by: Literal[
            "binom_fdr", "hyper_fdr", "binom_fold_enrichment", "hyper_fold_enrichment"
        ] = "binom_fdr",
        ascending: bool = True,
    ) -> pd.DataFrame:
        """Get top enriched terms.

        Args:
            ontology: Specific ontology or None for all.
            n: Number of top terms.
            sort_by: Column to sort by.
            ascending: Sort order (True for FDR, False for fold enrichment).

        Returns:
            DataFrame with top terms.
        """
        if ontology:
            df = self.results.get(ontology, pd.DataFrame())
            if not df.empty:
                df = df.copy()
                df["ontology"] = ontology
        else:
            dfs = []
            for onto, df in self.results.items():
                if df.empty:
                    continue
                df_copy = df.copy()
                df_copy["ontology"] = onto
                dfs.append(df_copy)
            df = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

        if df.empty:
            return df

        return df.sort_values(sort_by, ascending=ascending).head(n)

    def filter(
        self,
        max_fdr: float = 0.05,
        min_fold_enrichment: float = 1.0,
        min_genes: int = 2,
        test: Literal["binom", "hyper", "both"] = "both",
    ) -> EnrichmentResult:
        """Filter results by significance thresholds.

        Args:
            max_fdr: Maximum FDR threshold.
            min_fold_enrichment: Minimum fold enrichment.
            min_genes: Minimum number of genes.
            test: Which test to use for filtering.

        Returns:
            New EnrichmentResult with filtered data.
        """
        filtered = {}

        for ontology, df in self.results.items():
            if df.empty:
                filtered[ontology] = df.copy()
                continue

            mask = df["observed_genes"] >= min_genes

            if test in ("binom", "both"):
                mask &= df["binom_fdr"] <= max_fdr
                mask &= df["binom_fold_enrichment"] >= min_fold_enrichment

            if test in ("hyper", "both"):
                mask &= df["hyper_fdr"] <= max_fdr
                mask &= df["hyper_fold_enrichment"] >= min_fold_enrichment

            filtered[ontology] = df[mask].copy()

        return EnrichmentResult(
            results=filtered,
            job_id=self.job_id,
            species=self.species,
            rule=self.rule,
        )

    def to_dataframe(self, include_ontology: bool = True) -> pd.DataFrame:
        """Combine all results into single DataFrame.

        Args:
            include_ontology: If True, add 'ontology' column.

        Returns:
            Combined DataFrame with all results.
        """
        dfs = []
        for onto, df in self.results.items():
            if df.empty:
                continue
            df_copy = df.copy()
            if include_ontology:
                df_copy["ontology"] = onto
            dfs.append(df_copy)
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def summary(self) -> pd.DataFrame:
        """Get summary statistics for each ontology.

        Returns:
            DataFrame with summary per ontology.
        """
        data = []
        for ontology, df in self.results.items():
            n_total = len(df)
            n_sig = len(df[df["binom_fdr"] < 0.05]) if n_total > 0 else 0
            top_term = ""
            if n_sig > 0:
                top_term = df.nsmallest(1, "binom_fdr")["term_name"].iloc[0]

            data.append(
                {
                    "ontology": ontology,
                    "total_terms": n_total,
                    "significant_terms": n_sig,
                    "top_term": top_term,
                }
            )
        return pd.DataFrame(data)
