"""Gene annotation handling for local GREAT analysis.

Provides classes for loading and working with gene annotations,
particularly TSS (Transcription Start Site) positions needed
for the GREAT regulatory domain model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd


@dataclass
class Gene:
    """Represents a gene with its TSS and regulatory domain."""

    gene_id: str
    gene_name: str
    chrom: str
    tss: int
    strand: Literal["+", "-"]
    # Regulatory domain boundaries (computed by association rule)
    reg_start: int = 0
    reg_end: int = 0


@dataclass
class GeneAnnotation:
    """Collection of gene annotations for an organism.

    Attributes:
        genes: Dictionary mapping gene_id to Gene object.
        chrom_sizes: Dictionary mapping chromosome to size.
        organism: Organism name/identifier.
    """

    genes: dict[str, Gene] = field(default_factory=dict)
    chrom_sizes: dict[str, int] = field(default_factory=dict)
    organism: str = ""

    @classmethod
    def from_gtf(
        cls,
        gtf_path: str | Path,
        chrom_sizes: dict[str, int] | str | Path | None = None,
        feature_type: str = "gene",
        gene_id_attr: str = "gene_id",
        gene_name_attr: str = "gene_name",
    ) -> GeneAnnotation:
        """Load gene annotations from a GTF file.

        Args:
            gtf_path: Path to GTF/GFF file.
            chrom_sizes: Chromosome sizes as dict or path to .chrom.sizes file.
            feature_type: GTF feature type to extract (default: 'gene').
            gene_id_attr: Attribute name for gene ID.
            gene_name_attr: Attribute name for gene name.

        Returns:
            GeneAnnotation instance.
        """
        gtf_path = Path(gtf_path)

        # Load chromosome sizes
        sizes: dict[str, int] = {}
        if chrom_sizes is not None:
            if isinstance(chrom_sizes, dict):
                sizes = chrom_sizes
            else:
                sizes = cls._load_chrom_sizes(chrom_sizes)

        # Parse GTF
        genes: dict[str, Gene] = {}

        with open(gtf_path) as f:
            for line in f:
                if line.startswith("#"):
                    continue

                parts = line.strip().split("\t")
                if len(parts) < 9:
                    continue

                chrom, source, ftype, start, end, score, strand, frame, attrs = parts

                if ftype != feature_type:
                    continue

                # Parse attributes
                attr_dict = cls._parse_gtf_attributes(attrs)

                gene_id = attr_dict.get(gene_id_attr, "")
                gene_name = attr_dict.get(gene_name_attr, gene_id)

                if not gene_id:
                    continue

                # Determine TSS based on strand
                start_pos = int(start) - 1  # Convert to 0-based
                end_pos = int(end)
                tss = start_pos if strand == "+" else end_pos - 1

                # Skip if already seen (keep first occurrence)
                if gene_id in genes:
                    continue

                genes[gene_id] = Gene(
                    gene_id=gene_id,
                    gene_name=gene_name,
                    chrom=chrom,
                    tss=tss,
                    strand=strand,  # type: ignore[arg-type]
                )

        return cls(genes=genes, chrom_sizes=sizes, organism=gtf_path.stem)

    @classmethod
    def from_bed(
        cls,
        bed_path: str | Path,
        chrom_sizes: dict[str, int] | str | Path | None = None,
    ) -> GeneAnnotation:
        """Load gene annotations from a BED file.

        Expects BED6 format: chrom, start, end, name, score, strand.
        TSS is inferred from start (+ strand) or end (- strand).

        Args:
            bed_path: Path to BED file.
            chrom_sizes: Chromosome sizes.

        Returns:
            GeneAnnotation instance.
        """
        bed_path = Path(bed_path)

        # Load chromosome sizes
        sizes: dict[str, int] = {}
        if chrom_sizes is not None:
            if isinstance(chrom_sizes, dict):
                sizes = chrom_sizes
            else:
                sizes = cls._load_chrom_sizes(chrom_sizes)

        genes: dict[str, Gene] = {}

        with open(bed_path) as f:
            for line in f:
                if line.startswith("#") or line.startswith("track"):
                    continue

                parts = line.strip().split("\t")
                if len(parts) < 4:
                    continue

                chrom = parts[0]
                start = int(parts[1])
                end = int(parts[2])
                name = parts[3]
                strand = parts[5] if len(parts) > 5 else "+"

                # TSS based on strand
                tss = start if strand == "+" else end - 1

                if name not in genes:
                    genes[name] = Gene(
                        gene_id=name,
                        gene_name=name,
                        chrom=chrom,
                        tss=tss,
                        strand=strand,  # type: ignore[arg-type]
                    )

        return cls(genes=genes, chrom_sizes=sizes, organism=bed_path.stem)

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        chrom_sizes: dict[str, int] | None = None,
        chrom_col: str = "chrom",
        start_col: str = "start",
        end_col: str = "end",
        gene_id_col: str = "gene_id",
        gene_name_col: str | None = None,
        strand_col: str = "strand",
    ) -> GeneAnnotation:
        """Load gene annotations from a DataFrame.

        Args:
            df: DataFrame with gene annotations.
            chrom_sizes: Chromosome sizes.
            chrom_col: Column name for chromosome.
            start_col: Column name for start position.
            end_col: Column name for end position.
            gene_id_col: Column name for gene ID.
            gene_name_col: Column name for gene name (defaults to gene_id).
            strand_col: Column name for strand.

        Returns:
            GeneAnnotation instance.
        """
        genes: dict[str, Gene] = {}

        for _, row in df.iterrows():
            chrom = str(row[chrom_col])
            start = int(row[start_col])
            end = int(row[end_col])
            gene_id = str(row[gene_id_col])
            gene_name = str(row[gene_name_col]) if gene_name_col else gene_id
            strand = str(row.get(strand_col, "+"))

            tss = start if strand == "+" else end - 1

            if gene_id not in genes:
                genes[gene_id] = Gene(
                    gene_id=gene_id,
                    gene_name=gene_name,
                    chrom=chrom,
                    tss=tss,
                    strand=strand,  # type: ignore[arg-type]
                )

        return cls(genes=genes, chrom_sizes=chrom_sizes or {})

    @staticmethod
    def _parse_gtf_attributes(attrs_str: str) -> dict[str, str]:
        """Parse GTF attribute string into dictionary."""
        attrs = {}
        for attr in attrs_str.strip().rstrip(";").split(";"):
            attr = attr.strip()
            if not attr:
                continue
            # Handle both GTF (key "value") and GFF3 (key=value) formats
            if "=" in attr:
                key, value = attr.split("=", 1)
            elif " " in attr:
                key, value = attr.split(" ", 1)
                value = value.strip('"')
            else:
                continue
            attrs[key.strip()] = value.strip().strip('"')
        return attrs

    @staticmethod
    def _load_chrom_sizes(path: str | Path) -> dict[str, int]:
        """Load chromosome sizes from a file."""
        sizes = {}
        with open(path) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    sizes[parts[0]] = int(parts[1])
        return sizes

    def get_genes_by_chrom(self, chrom: str) -> list[Gene]:
        """Get all genes on a chromosome, sorted by TSS."""
        genes = [g for g in self.genes.values() if g.chrom == chrom]
        return sorted(genes, key=lambda g: g.tss)

    def get_all_chromosomes(self) -> list[str]:
        """Get list of all chromosomes with genes."""
        return sorted(set(g.chrom for g in self.genes.values()))

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame."""
        data = []
        for gene in self.genes.values():
            data.append({
                "gene_id": gene.gene_id,
                "gene_name": gene.gene_name,
                "chrom": gene.chrom,
                "tss": gene.tss,
                "strand": gene.strand,
                "reg_start": gene.reg_start,
                "reg_end": gene.reg_end,
            })
        return pd.DataFrame(data)

    def __len__(self) -> int:
        return len(self.genes)

    def __contains__(self, gene_id: str) -> bool:
        return gene_id in self.genes

    def __getitem__(self, gene_id: str) -> Gene:
        return self.genes[gene_id]


def compute_regulatory_domains(
    annotation: GeneAnnotation,
    rule: Literal["basalPlusExt", "twoClosest", "oneClosest"] = "basalPlusExt",
    upstream: int = 5000,
    downstream: int = 1000,
    max_extension: int = 1_000_000,
) -> GeneAnnotation:
    """Compute regulatory domains for all genes.

    Modifies genes in-place to set reg_start and reg_end.

    Args:
        annotation: Gene annotation object.
        rule: Association rule:
            - basalPlusExt: Basal domain with extension
            - twoClosest: Two closest genes
            - oneClosest: One closest gene
        upstream: Upstream basal domain (bp).
        downstream: Downstream basal domain (bp).
        max_extension: Maximum extension distance (bp).

    Returns:
        The same GeneAnnotation with regulatory domains computed.
    """
    for chrom in annotation.get_all_chromosomes():
        genes = annotation.get_genes_by_chrom(chrom)
        chrom_size = annotation.chrom_sizes.get(chrom, 300_000_000)

        if rule == "basalPlusExt":
            _compute_basal_plus_ext(
                genes, chrom_size, upstream, downstream, max_extension
            )
        elif rule == "twoClosest":
            _compute_two_closest(genes, chrom_size, max_extension)
        elif rule == "oneClosest":
            _compute_one_closest(genes, chrom_size, max_extension)
        else:
            raise ValueError(f"Unknown rule: {rule}")

    return annotation


def _compute_basal_plus_ext(
    genes: list[Gene],
    chrom_size: int,
    upstream: int,
    downstream: int,
    max_extension: int,
) -> None:
    """Compute basal plus extension regulatory domains."""
    n = len(genes)
    if n == 0:
        return

    for i, gene in enumerate(genes):
        # Basal domain
        if gene.strand == "+":
            basal_start = gene.tss - upstream
            basal_end = gene.tss + downstream
        else:
            basal_start = gene.tss - downstream
            basal_end = gene.tss + upstream

        # Extension limits
        ext_start = max(0, gene.tss - max_extension)
        ext_end = min(chrom_size, gene.tss + max_extension)

        # Extend until hitting another gene's basal domain
        # Left extension
        reg_start = max(basal_start, ext_start)
        if i > 0:
            prev_gene = genes[i - 1]
            prev_basal_end = (
                prev_gene.tss + downstream
                if prev_gene.strand == "+"
                else prev_gene.tss + upstream
            )
            reg_start = max(reg_start, prev_basal_end)

        # Right extension
        reg_end = min(basal_end, ext_end)
        if i < n - 1:
            next_gene = genes[i + 1]
            next_basal_start = (
                next_gene.tss - upstream
                if next_gene.strand == "+"
                else next_gene.tss - downstream
            )
            # Extend right until next gene's basal start
            reg_end = max(reg_end, min(ext_end, next_basal_start))

        # Ensure within bounds
        gene.reg_start = max(0, reg_start)
        gene.reg_end = min(chrom_size, reg_end)


def _compute_two_closest(
    genes: list[Gene],
    chrom_size: int,
    max_extension: int,
) -> None:
    """Compute two closest genes regulatory domains."""
    n = len(genes)
    if n == 0:
        return

    for i, gene in enumerate(genes):
        # Find midpoint to previous gene
        if i > 0:
            prev_tss = genes[i - 1].tss
            mid_left = (gene.tss + prev_tss) // 2
            reg_start = max(0, mid_left, gene.tss - max_extension)
        else:
            reg_start = max(0, gene.tss - max_extension)

        # Find midpoint to next gene
        if i < n - 1:
            next_tss = genes[i + 1].tss
            mid_right = (gene.tss + next_tss) // 2
            reg_end = min(chrom_size, mid_right, gene.tss + max_extension)
        else:
            reg_end = min(chrom_size, gene.tss + max_extension)

        gene.reg_start = reg_start
        gene.reg_end = reg_end


def _compute_one_closest(
    genes: list[Gene],
    chrom_size: int,
    max_extension: int,
) -> None:
    """Compute one closest gene regulatory domains."""
    # Same as two closest for now (simple midpoint model)
    _compute_two_closest(genes, chrom_size, max_extension)
