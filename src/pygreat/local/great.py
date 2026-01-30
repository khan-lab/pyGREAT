"""Local GREAT analysis implementation.

Implements the GREAT algorithm for genomic region enrichment analysis
without requiring the Stanford server.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from pygreat.local.genes import (
    Gene,
    GeneAnnotation,
    compute_regulatory_domains,
)
from pygreat.local.genesets import GeneSet, GeneSetCollection
from pygreat.local.stats import (
    binomial_test,
    correct_pvalues,
    hypergeometric_test,
)
from pygreat.models.regions import GenomicRegions


@dataclass
class LocalGreatResult:
    """Results from local GREAT analysis.

    Attributes:
        enrichment_tables: Dictionary mapping ontology name to enrichment DataFrame.
        region_gene_associations: DataFrame of region-gene associations.
        metadata: Analysis metadata.
    """

    enrichment_tables: dict[str, pd.DataFrame] = field(default_factory=dict)
    region_gene_associations: pd.DataFrame = field(
        default_factory=lambda: pd.DataFrame()
    )
    metadata: dict[str, str] = field(default_factory=dict)

    def get_enrichment_tables(
        self,
        ontologies: list[str] | None = None,
        *,
        min_genes: int = 1,
        max_fdr: float = 1.0,
    ) -> dict[str, pd.DataFrame]:
        """Get enrichment tables with optional filtering.

        Args:
            ontologies: List of ontology names. None = all.
            min_genes: Minimum observed genes.
            max_fdr: Maximum FDR threshold.

        Returns:
            Dictionary of filtered enrichment DataFrames.
        """
        target = ontologies or list(self.enrichment_tables.keys())
        results = {}

        for ont in target:
            if ont not in self.enrichment_tables:
                continue

            df = self.enrichment_tables[ont].copy()

            if not df.empty:
                if "observed_genes" in df.columns:
                    df = df[df["observed_genes"] >= min_genes]
                if "binom_fdr" in df.columns:
                    df = df[df["binom_fdr"] <= max_fdr]

            results[ont] = df

        return results

    def to_dataframe(self, ontology: str | None = None) -> pd.DataFrame:
        """Export results to DataFrame.

        Args:
            ontology: Specific ontology or None for all.

        Returns:
            Combined DataFrame with 'ontology' column if exporting all.
        """
        if ontology:
            return self.enrichment_tables.get(ontology, pd.DataFrame()).copy()

        dfs = []
        for ont_name, df in self.enrichment_tables.items():
            if not df.empty:
                ont_df = df.copy()
                ont_df.insert(0, "ontology", ont_name)
                dfs.append(ont_df)

        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


class LocalGreat:
    """Local GREAT analysis engine.

    Performs GREAT enrichment analysis locally without requiring
    the Stanford server. Supports any organism and custom gene sets.

    Example:
        >>> from pygreat.local import LocalGreat
        >>> from pygreat.local.genes import GeneAnnotation
        >>> from pygreat.local.genesets import GeneSetCollection
        >>>
        >>> # Load gene annotations
        >>> genes = GeneAnnotation.from_gtf("genes.gtf", chrom_sizes="genome.chrom.sizes")
        >>>
        >>> # Load gene sets
        >>> go_bp = GeneSetCollection.from_gmt("go_bp.gmt")
        >>>
        >>> # Run analysis
        >>> great = LocalGreat(genes, {"GO Biological Process": go_bp})
        >>> result = great.analyze("peaks.bed")
        >>> print(result.get_enrichment_tables(max_fdr=0.05))
    """

    def __init__(
        self,
        gene_annotation: GeneAnnotation,
        gene_sets: dict[str, GeneSetCollection],
        rule: Literal["basalPlusExt", "twoClosest", "oneClosest"] = "basalPlusExt",
        upstream: int = 5000,
        downstream: int = 1000,
        max_extension: int = 1_000_000,
    ) -> None:
        """Initialize LocalGreat engine.

        Args:
            gene_annotation: Gene annotations with TSS positions.
            gene_sets: Dictionary of gene set collections by name.
            rule: Association rule for linking regions to genes.
            upstream: Upstream basal domain (bp).
            downstream: Downstream basal domain (bp).
            max_extension: Maximum extension distance (bp).
        """
        self.gene_annotation = gene_annotation
        self.gene_sets = gene_sets
        self.rule = rule
        self.upstream = upstream
        self.downstream = downstream
        self.max_extension = max_extension

        # Compute regulatory domains
        compute_regulatory_domains(
            self.gene_annotation,
            rule=rule,
            upstream=upstream,
            downstream=downstream,
            max_extension=max_extension,
        )

        # Build chromosome-indexed gene lookup
        self._genes_by_chrom: dict[str, list[Gene]] = {}
        for chrom in self.gene_annotation.get_all_chromosomes():
            self._genes_by_chrom[chrom] = self.gene_annotation.get_genes_by_chrom(chrom)

        # Build gene name to ID mapping for flexible matching
        self._name_to_id: dict[str, str] = {}
        self._id_to_name: dict[str, str] = {}
        for gene_id, gene in self.gene_annotation.genes.items():
            self._name_to_id[gene.gene_name] = gene_id
            self._name_to_id[gene_id] = gene_id  # Also map ID to itself
            self._id_to_name[gene_id] = gene.gene_name

        # Translate gene sets to use gene IDs (GMT files often use gene names)
        self._translate_gene_sets()

        # Calculate total genome coverage by gene regulatory domains
        self._total_genome_size = self._calculate_total_genome_size()
        self._total_genes = len(self.gene_annotation)

    def _translate_gene_sets(self) -> None:
        """Translate gene names in gene sets to gene IDs.

        GMT files often use gene symbols (names) rather than IDs.
        This method converts them to match the annotation's gene_id keys.
        """
        for collection in self.gene_sets.values():
            for gene_set in collection.gene_sets.values():
                translated_genes: set[str] = set()
                for gene_name in gene_set.genes:
                    # Try to find the gene ID for this name
                    if gene_name in self._name_to_id:
                        translated_genes.add(self._name_to_id[gene_name])
                    # Keep original if not found (might already be an ID)
                    elif gene_name in self.gene_annotation.genes:
                        translated_genes.add(gene_name)
                    # else: gene not in annotation, skip it
                gene_set.genes = translated_genes

    def _calculate_total_genome_size(self) -> int:
        """Calculate total size of regulatory domain-covered genome."""
        total = 0
        for genes in self._genes_by_chrom.values():
            for gene in genes:
                total += gene.reg_end - gene.reg_start
        return max(total, 1)

    def analyze(
        self,
        regions: str | Path | pd.DataFrame | GenomicRegions,
        background: str | Path | pd.DataFrame | GenomicRegions | None = None,
        min_genes_per_term: int = 1,
        max_genes_per_term: int = 10000,
    ) -> LocalGreatResult:
        """Run GREAT enrichment analysis.

        Args:
            regions: Input genomic regions (BED file, DataFrame, or GenomicRegions).
            background: Optional background regions for foreground/background test.
            min_genes_per_term: Minimum genes per term to test.
            max_genes_per_term: Maximum genes per term to test.

        Returns:
            LocalGreatResult with enrichment tables and associations.
        """
        # Load regions
        if isinstance(regions, (str, Path)):
            regions = GenomicRegions.from_bed(regions)
        elif isinstance(regions, pd.DataFrame):
            regions = GenomicRegions.from_dataframe(regions)

        # Associate regions with genes
        region_genes = self._associate_regions_to_genes(regions)

        # Get unique genes hit by regions
        all_hit_genes: set[str] = set()
        for genes in region_genes.values():
            all_hit_genes.update(genes)

        # Calculate genome fraction for each gene set term
        term_genome_fractions = self._calculate_genome_fractions()

        # Run enrichment tests for each gene set collection
        enrichment_tables: dict[str, pd.DataFrame] = {}

        for collection_name, collection in self.gene_sets.items():
            # Filter by size
            filtered = collection.filter_by_size(min_genes_per_term, max_genes_per_term)

            results = self._test_enrichment(
                regions=regions,
                region_genes=region_genes,
                hit_genes=all_hit_genes,
                collection=filtered,
                genome_fractions=term_genome_fractions.get(collection_name, {}),
            )

            if not results.empty:
                enrichment_tables[collection_name] = results

        # Build region-gene association table
        assoc_rows = []
        for region_key, genes in region_genes.items():
            for gene_id in genes:
                gene = self.gene_annotation.genes.get(gene_id)
                if gene:
                    assoc_rows.append({
                        "region": region_key,
                        "gene_id": gene_id,
                        "gene_name": gene.gene_name,
                        "chrom": gene.chrom,
                        "tss": gene.tss,
                    })

        associations_df = pd.DataFrame(assoc_rows)

        # Metadata
        metadata = {
            "rule": self.rule,
            "upstream": str(self.upstream),
            "downstream": str(self.downstream),
            "max_extension": str(self.max_extension),
            "n_regions": str(len(regions)),
            "n_genes_hit": str(len(all_hit_genes)),
        }

        return LocalGreatResult(
            enrichment_tables=enrichment_tables,
            region_gene_associations=associations_df,
            metadata=metadata,
        )

    def _associate_regions_to_genes(
        self,
        regions: GenomicRegions,
    ) -> dict[str, set[str]]:
        """Associate each region with genes whose regulatory domains it overlaps.

        Args:
            regions: Input genomic regions.

        Returns:
            Dictionary mapping region key to set of gene IDs.
        """
        region_genes: dict[str, set[str]] = {}

        for region in regions:
            chrom = region.chrom
            start = region.start
            end = region.end
            name = region.name

            region_key = f"{chrom}:{start}-{end}"
            if name:
                region_key = f"{region_key}:{name}"

            genes_hit: set[str] = set()

            # Get genes on this chromosome
            chrom_genes = self._genes_by_chrom.get(chrom, [])

            # Find overlapping genes (binary search could optimize this)
            for gene in chrom_genes:
                # Check if region overlaps gene's regulatory domain
                if start < gene.reg_end and end > gene.reg_start:
                    genes_hit.add(gene.gene_id)

            region_genes[region_key] = genes_hit

        return region_genes

    def _calculate_genome_fractions(self) -> dict[str, dict[str, float]]:
        """Calculate genome fraction covered by each term's genes.

        Returns:
            Nested dict: collection_name -> term_id -> genome_fraction.
        """
        fractions: dict[str, dict[str, float]] = {}

        for collection_name, collection in self.gene_sets.items():
            fractions[collection_name] = {}

            for term_id, gene_set in collection.gene_sets.items():
                # Sum regulatory domain sizes for genes in this term
                term_coverage = 0
                for gene_id in gene_set.genes:
                    if gene_id in self.gene_annotation.genes:
                        gene = self.gene_annotation.genes[gene_id]
                        term_coverage += gene.reg_end - gene.reg_start

                fraction = term_coverage / self._total_genome_size
                fractions[collection_name][term_id] = fraction

        return fractions

    def _test_enrichment(
        self,
        regions: GenomicRegions,
        region_genes: dict[str, set[str]],
        hit_genes: set[str],
        collection: GeneSetCollection,
        genome_fractions: dict[str, float],
    ) -> pd.DataFrame:
        """Run enrichment tests for a gene set collection.

        Args:
            regions: Input regions.
            region_genes: Region to gene mapping.
            hit_genes: All genes hit by any region.
            collection: Gene set collection to test.
            genome_fractions: Pre-computed genome fractions.

        Returns:
            DataFrame with enrichment results.
        """
        n_regions = len(regions)
        n_hit_genes = len(hit_genes)

        results = []

        for term_id, gene_set in collection.gene_sets.items():
            # Count regions hitting genes in this term
            term_genes = gene_set.genes
            regions_hitting_term = 0

            for region_key, genes in region_genes.items():
                if genes & term_genes:  # Intersection
                    regions_hitting_term += 1

            # Count genes in both hit_genes and term
            genes_in_term_hit = len(hit_genes & term_genes)

            # Skip if no hits
            if regions_hitting_term == 0 and genes_in_term_hit == 0:
                continue

            # Binomial test
            genome_fraction = genome_fractions.get(term_id, 0.0)
            binom_p, binom_fold = binomial_test(
                observed_regions=regions_hitting_term,
                total_regions=n_regions,
                genome_fraction=genome_fraction,
            )

            # Hypergeometric test
            hyper_p, hyper_fold = hypergeometric_test(
                observed_genes=genes_in_term_hit,
                total_genes_in_regions=n_hit_genes,
                genes_in_term=len(term_genes),
                total_genes_in_genome=self._total_genes,
            )

            results.append({
                "term_id": term_id,
                "term_name": gene_set.name,
                "binom_p": binom_p,
                "binom_fold_enrichment": binom_fold,
                "observed_regions": regions_hitting_term,
                "expected_regions": n_regions * genome_fraction,
                "genome_fraction": genome_fraction,
                "hyper_p": hyper_p,
                "hyper_fold_enrichment": hyper_fold,
                "observed_genes": genes_in_term_hit,
                "expected_genes": (n_hit_genes * len(term_genes)) / self._total_genes,
                "total_genes": len(term_genes),
            })

        if not results:
            return pd.DataFrame()

        df = pd.DataFrame(results)

        # Apply FDR correction
        df["binom_fdr"] = correct_pvalues(np.array(df["binom_p"]))
        df["hyper_fdr"] = correct_pvalues(np.array(df["hyper_p"]))

        # Add Bonferroni
        n_tests = len(df)
        df["binom_bonferroni"] = np.minimum(df["binom_p"] * n_tests, 1.0)
        df["hyper_bonferroni"] = np.minimum(df["hyper_p"] * n_tests, 1.0)

        # Sort by binomial p-value
        df = df.sort_values("binom_p").reset_index(drop=True)

        # Add ranks
        df["binom_rank"] = range(1, len(df) + 1)
        df["hyper_rank"] = df["hyper_p"].rank().astype(int)

        # Reorder columns
        cols = [
            "term_id",
            "term_name",
            "binom_rank",
            "binom_p",
            "binom_bonferroni",
            "binom_fdr",
            "binom_fold_enrichment",
            "observed_regions",
            "expected_regions",
            "genome_fraction",
            "hyper_rank",
            "hyper_p",
            "hyper_bonferroni",
            "hyper_fdr",
            "hyper_fold_enrichment",
            "observed_genes",
            "expected_genes",
            "total_genes",
        ]
        df = df[[c for c in cols if c in df.columns]]

        return df

    @classmethod
    def from_gtf(
        cls,
        gtf_path: str | Path,
        gmt_paths: dict[str, str | Path],
        chrom_sizes: dict[str, int] | str | Path | None = None,
        **kwargs: Any,
    ) -> LocalGreat:
        """Create LocalGreat from GTF and GMT files.

        Args:
            gtf_path: Path to GTF file with gene annotations.
            gmt_paths: Dictionary mapping collection name to GMT file path.
            chrom_sizes: Chromosome sizes (dict or file path).
            **kwargs: Additional arguments passed to __init__.

        Returns:
            Configured LocalGreat instance.
        """
        # Load gene annotations
        gene_annotation = GeneAnnotation.from_gtf(gtf_path, chrom_sizes=chrom_sizes)

        # Load gene sets
        gene_sets = {}
        for name, gmt_path in gmt_paths.items():
            gene_sets[name] = GeneSetCollection.from_gmt(gmt_path, name=name)

        return cls(gene_annotation, gene_sets, **kwargs)
