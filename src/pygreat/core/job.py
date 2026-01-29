"""GreatJob class for managing job results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import pandas as pd

from pygreat.core.config import DEFAULT_ONTOLOGIES

if TYPE_CHECKING:
    from pygreat.core.client import GreatClient


@dataclass
class GreatJob:
    """Represents a completed GREAT job with enrichment results.

    This class provides methods to access and filter enrichment results
    that were retrieved from the GREAT batch API.

    Attributes:
        job_id: Identifier (typically the hosted file URL).
        client: Reference to the GREAT client.
        ontologies: Available ontology categories.
        species: Genome assembly used.
        rule: Association rule used.
        job_name: Optional user-provided name.
        enrichment_results: Pre-fetched enrichment DataFrames by ontology.
        metadata: Batch response metadata (version, species, rule).
        ontology_stats: Summary statistics per ontology.

    Example:
        >>> job = client.submit_job("peaks.bed", species="hg38")
        >>> results = job.get_enrichment_tables()
        >>> go_bp = results["GO Biological Process"]
        >>> print(go_bp[go_bp["binom_fdr"] < 0.05])
    """

    job_id: str
    client: GreatClient
    ontologies: dict[str, list[str]] = field(default_factory=dict)
    species: str = ""
    rule: str = ""
    job_name: str | None = None
    enrichment_results: dict[str, pd.DataFrame] = field(
        default_factory=dict, repr=False
    )
    metadata: dict[str, str] = field(default_factory=dict, repr=False)
    ontology_stats: dict[str, dict[str, Any]] = field(
        default_factory=dict, repr=False
    )

    def get_enrichment_tables(
        self,
        ontologies: list[str] | None = None,
        *,
        min_genes: int = 1,
        max_fdr: float = 1.0,
    ) -> dict[str, pd.DataFrame]:
        """Retrieve enrichment results for specified ontologies.

        Args:
            ontologies: List of ontology names to retrieve. If None,
                retrieves all available ontologies.
            min_genes: Minimum number of observed genes for a term.
            max_fdr: Maximum FDR threshold for filtering.

        Returns:
            Dictionary mapping ontology names to result DataFrames.
            Each DataFrame contains columns:
            - term_id: Ontology term identifier
            - term_name: Human-readable term name
            - binom_p: Binomial p-value
            - binom_fdr: Binomial FDR
            - binom_fold_enrichment: Binomial fold enrichment
            - hyper_p: Hypergeometric p-value
            - hyper_fdr: Hypergeometric FDR
            - hyper_fold_enrichment: Hypergeometric fold enrichment
            - observed_genes: Number of observed genes
            - total_genes: Total genes in term
            - observed_regions: Number of observed regions

        Example:
            >>> results = job.get_enrichment_tables()
            >>> # Get specific ontologies
            >>> results = job.get_enrichment_tables(
            ...     ontologies=["GO Biological Process", "GO Molecular Function"]
            ... )
            >>> # Filter significant terms
            >>> results = job.get_enrichment_tables(max_fdr=0.05, min_genes=5)
        """
        # Determine which ontologies to return
        if ontologies is not None:
            target_ontologies = ontologies
        else:
            # Return all available ontologies
            target_ontologies = list(self.enrichment_results.keys())
            if not target_ontologies:
                target_ontologies = list(DEFAULT_ONTOLOGIES)

        results: dict[str, pd.DataFrame] = {}

        for ontology in target_ontologies:
            if ontology in self.enrichment_results:
                df = self.enrichment_results[ontology]

                # Apply filters
                if not df.empty:
                    filtered = df.copy()
                    if "observed_genes" in filtered.columns:
                        filtered = filtered[filtered["observed_genes"] >= min_genes]
                    if "binom_fdr" in filtered.columns:
                        filtered = filtered[filtered["binom_fdr"] <= max_fdr]
                    results[ontology] = filtered
                else:
                    results[ontology] = df
            else:
                # Return empty DataFrame for requested but unavailable ontologies
                results[ontology] = pd.DataFrame()

        return results

    def get_enrichment_table(
        self,
        ontology: str,
        *,
        min_genes: int = 1,
        max_fdr: float = 1.0,
    ) -> pd.DataFrame:
        """Retrieve enrichment results for a single ontology.

        Args:
            ontology: Name of the ontology (e.g., 'GO Biological Process').
            min_genes: Minimum number of observed genes for a term.
            max_fdr: Maximum FDR threshold for filtering.

        Returns:
            DataFrame with enrichment results.

        Example:
            >>> go_bp = job.get_enrichment_table("GO Biological Process")
            >>> significant = job.get_enrichment_table(
            ...     "GO Biological Process", max_fdr=0.05
            ... )
        """
        results = self.get_enrichment_tables(
            ontologies=[ontology],
            min_genes=min_genes,
            max_fdr=max_fdr,
        )
        return results.get(ontology, pd.DataFrame())

    def available_ontologies(self) -> dict[str, list[str]]:
        """Return available ontology categories and their ontologies.

        Returns:
            Dictionary mapping category names to lists of ontology names.

        Example:
            >>> ontologies = job.available_ontologies()
            >>> for category, names in ontologies.items():
            ...     print(f"{category}: {names}")
        """
        return self.ontologies.copy()

    def list_ontologies(self) -> list[str]:
        """Return flat list of all available ontology names.

        Returns:
            List of ontology names.

        Example:
            >>> ontologies = job.list_ontologies()
            >>> print(ontologies)
            ['Ensembl Genes', 'GO Biological Process', ...]
        """
        return list(self.enrichment_results.keys())

    def get_metadata(self) -> dict[str, str]:
        """Return job metadata from GREAT response.

        Returns:
            Dictionary with version, species, and rule info.

        Example:
            >>> meta = job.get_metadata()
            >>> print(f"GREAT version: {meta['version']}")
        """
        return self.metadata.copy()

    def get_ontology_stats(self) -> dict[str, dict[str, Any]]:
        """Return ontology summary statistics.

        Returns:
            Dictionary mapping ontology names to stats (terms tested, etc.).

        Example:
            >>> stats = job.get_ontology_stats()
            >>> print(stats["GO Biological Process"]["terms_tested"])
        """
        return self.ontology_stats.copy()

    def to_dataframe(self, ontology: str | None = None) -> pd.DataFrame:
        """Export results as a single DataFrame.

        Args:
            ontology: Specific ontology to export. If None, exports all
                ontologies with an 'ontology' column added.

        Returns:
            DataFrame with enrichment results.

        Example:
            >>> # Export single ontology
            >>> df = job.to_dataframe("GO Biological Process")
            >>> # Export all ontologies
            >>> df = job.to_dataframe()
            >>> df.to_csv("results.tsv", sep="\\t", index=False)
        """
        if ontology is not None:
            return self.enrichment_results.get(ontology, pd.DataFrame()).copy()

        # Combine all ontologies
        dfs = []
        for ont_name, df in self.enrichment_results.items():
            if not df.empty:
                ont_df = df.copy()
                ont_df.insert(0, "ontology", ont_name)
                dfs.append(ont_df)

        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

    def __repr__(self) -> str:
        name_part = f", job_name={self.job_name!r}" if self.job_name else ""
        n_ontologies = len(self.enrichment_results)
        return (
            f"GreatJob(species={self.species!r}, "
            f"rule={self.rule!r}, "
            f"ontologies={n_ontologies}{name_part})"
        )
