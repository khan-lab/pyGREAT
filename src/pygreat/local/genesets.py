"""Gene set collections for local GREAT analysis.

Provides classes for loading and working with gene set collections
from various sources: GMT files, GO ontology, MSigDB, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import pandas as pd


@dataclass
class GeneSet:
    """A single gene set/term."""

    id: str
    name: str
    genes: set[str]
    description: str = ""
    ontology: str = ""

    def __len__(self) -> int:
        return len(self.genes)

    def __contains__(self, gene: str) -> bool:
        return gene in self.genes


@dataclass
class GeneSetCollection:
    """Collection of gene sets, typically from one ontology.

    Attributes:
        name: Collection name (e.g., "GO Biological Process").
        gene_sets: Dictionary mapping term ID to GeneSet.
        description: Optional description.
    """

    name: str
    gene_sets: dict[str, GeneSet] = field(default_factory=dict)
    description: str = ""

    @classmethod
    def from_gmt(
        cls,
        gmt_path: str | Path,
        name: str | None = None,
    ) -> GeneSetCollection:
        """Load gene sets from a GMT file.

        GMT format: term_id<TAB>description<TAB>gene1<TAB>gene2<TAB>...

        Args:
            gmt_path: Path to GMT file.
            name: Collection name (defaults to filename).

        Returns:
            GeneSetCollection instance.
        """
        gmt_path = Path(gmt_path)
        collection_name = name or gmt_path.stem

        gene_sets: dict[str, GeneSet] = {}

        with open(gmt_path) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) < 3:
                    continue

                term_id = parts[0]
                description = parts[1]
                genes = set(parts[2:])

                # Use description as name if it looks like one
                term_name = description if description else term_id

                gene_sets[term_id] = GeneSet(
                    id=term_id,
                    name=term_name,
                    genes=genes,
                    description=description,
                    ontology=collection_name,
                )

        return cls(name=collection_name, gene_sets=gene_sets)

    @classmethod
    def from_dict(
        cls,
        gene_sets_dict: dict[str, set[str]],
        name: str = "Custom",
    ) -> GeneSetCollection:
        """Create collection from a dictionary.

        Args:
            gene_sets_dict: Dictionary mapping term ID to set of genes.
            name: Collection name.

        Returns:
            GeneSetCollection instance.
        """
        gene_sets: dict[str, GeneSet] = {}

        for term_id, genes in gene_sets_dict.items():
            gene_sets[term_id] = GeneSet(
                id=term_id,
                name=term_id,
                genes=set(genes),
                ontology=name,
            )

        return cls(name=name, gene_sets=gene_sets)

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        term_col: str = "term",
        gene_col: str = "gene",
        name_col: str | None = None,
        collection_name: str = "Custom",
    ) -> GeneSetCollection:
        """Create collection from a DataFrame.

        DataFrame should have one row per term-gene pair.

        Args:
            df: DataFrame with term-gene mappings.
            term_col: Column name for term ID.
            gene_col: Column name for gene.
            name_col: Column name for term name (optional).
            collection_name: Collection name.

        Returns:
            GeneSetCollection instance.
        """
        gene_sets: dict[str, GeneSet] = {}

        for term_id, group in df.groupby(term_col):
            term_id = str(term_id)
            genes = set(group[gene_col].astype(str))

            if name_col and name_col in group.columns:
                term_name = str(group[name_col].iloc[0])
            else:
                term_name = term_id

            gene_sets[term_id] = GeneSet(
                id=term_id,
                name=term_name,
                genes=genes,
                ontology=collection_name,
            )

        return cls(name=collection_name, gene_sets=gene_sets)

    def filter_by_size(
        self,
        min_size: int = 1,
        max_size: int = 10000,
    ) -> GeneSetCollection:
        """Filter gene sets by size.

        Args:
            min_size: Minimum number of genes.
            max_size: Maximum number of genes.

        Returns:
            New filtered GeneSetCollection.
        """
        filtered = {
            term_id: gs
            for term_id, gs in self.gene_sets.items()
            if min_size <= len(gs) <= max_size
        }
        return GeneSetCollection(
            name=self.name,
            gene_sets=filtered,
            description=self.description,
        )

    def get_all_genes(self) -> set[str]:
        """Get the union of all genes across all gene sets."""
        all_genes: set[str] = set()
        for gs in self.gene_sets.values():
            all_genes.update(gs.genes)
        return all_genes

    def to_gmt(self, path: str | Path) -> None:
        """Save collection to GMT format.

        Args:
            path: Output file path.
        """
        with open(path, "w") as f:
            for gs in self.gene_sets.values():
                genes_str = "\t".join(sorted(gs.genes))
                f.write(f"{gs.id}\t{gs.description}\t{genes_str}\n")

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame with one row per term-gene pair."""
        rows = []
        for gs in self.gene_sets.values():
            for gene in gs.genes:
                rows.append({
                    "term_id": gs.id,
                    "term_name": gs.name,
                    "gene": gene,
                    "ontology": gs.ontology,
                })
        return pd.DataFrame(rows)

    def __len__(self) -> int:
        return len(self.gene_sets)

    def __contains__(self, term_id: str) -> bool:
        return term_id in self.gene_sets

    def __getitem__(self, term_id: str) -> GeneSet:
        return self.gene_sets[term_id]

    def __iter__(self) -> Iterator[GeneSet]:
        return iter(self.gene_sets.values())


def load_go_from_gaf(
    gaf_path: str | Path,
    obo_path: str | Path | None = None,
) -> dict[str, GeneSetCollection]:
    """Load Gene Ontology annotations from a GAF file.

    Args:
        gaf_path: Path to GAF (Gene Association Format) file.
        obo_path: Optional path to OBO file for term names.

    Returns:
        Dictionary with 'GO Biological Process', 'GO Molecular Function',
        'GO Cellular Component' collections.
    """
    gaf_path = Path(gaf_path)

    # Parse OBO for term names if provided
    term_names: dict[str, str] = {}
    term_namespace: dict[str, str] = {}

    if obo_path:
        term_names, term_namespace = _parse_obo(obo_path)

    # Parse GAF
    go_bp: dict[str, set[str]] = {}
    go_mf: dict[str, set[str]] = {}
    go_cc: dict[str, set[str]] = {}

    with open(gaf_path) as f:
        for line in f:
            if line.startswith("!"):
                continue

            parts = line.strip().split("\t")
            if len(parts) < 5:
                continue

            gene_symbol = parts[2]  # DB Object Symbol
            go_id = parts[4]  # GO ID
            aspect = parts[8] if len(parts) > 8 else ""

            # Determine namespace from aspect or OBO
            if aspect == "P" or term_namespace.get(go_id) == "biological_process":
                if go_id not in go_bp:
                    go_bp[go_id] = set()
                go_bp[go_id].add(gene_symbol)
            elif aspect == "F" or term_namespace.get(go_id) == "molecular_function":
                if go_id not in go_mf:
                    go_mf[go_id] = set()
                go_mf[go_id].add(gene_symbol)
            elif aspect == "C" or term_namespace.get(go_id) == "cellular_component":
                if go_id not in go_cc:
                    go_cc[go_id] = set()
                go_cc[go_id].add(gene_symbol)

    # Build collections
    collections = {}

    for name, go_dict in [
        ("GO Biological Process", go_bp),
        ("GO Molecular Function", go_mf),
        ("GO Cellular Component", go_cc),
    ]:
        gene_sets = {}
        for go_id, genes in go_dict.items():
            gene_sets[go_id] = GeneSet(
                id=go_id,
                name=term_names.get(go_id, go_id),
                genes=genes,
                ontology=name,
            )
        collections[name] = GeneSetCollection(name=name, gene_sets=gene_sets)

    return collections


def _parse_obo(obo_path: str | Path) -> tuple[dict[str, str], dict[str, str]]:
    """Parse OBO file for term names and namespaces.

    Returns:
        Tuple of (term_names, term_namespace) dictionaries.
    """
    term_names: dict[str, str] = {}
    term_namespace: dict[str, str] = {}

    current_id = ""
    current_name = ""
    current_ns = ""

    with open(obo_path) as f:
        for line in f:
            line = line.strip()

            if line == "[Term]":
                # Save previous term
                if current_id:
                    term_names[current_id] = current_name
                    term_namespace[current_id] = current_ns
                current_id = ""
                current_name = ""
                current_ns = ""

            elif line.startswith("id: GO:"):
                current_id = line[4:]
            elif line.startswith("name: "):
                current_name = line[6:]
            elif line.startswith("namespace: "):
                current_ns = line[11:]

        # Save last term
        if current_id:
            term_names[current_id] = current_name
            term_namespace[current_id] = current_ns

    return term_names, term_namespace


def load_msigdb_gmt(gmt_path: str | Path) -> dict[str, GeneSetCollection]:
    """Load MSigDB gene sets from GMT file.

    Automatically categorizes gene sets by their prefix (e.g., HALLMARK, KEGG).

    Args:
        gmt_path: Path to MSigDB GMT file.

    Returns:
        Dictionary of categorized GeneSetCollections.
    """
    gmt_path = Path(gmt_path)

    # Load all gene sets first
    all_sets = GeneSetCollection.from_gmt(gmt_path)

    # Categorize by prefix
    categories: dict[str, dict[str, GeneSet]] = {}

    for gs in all_sets.gene_sets.values():
        # Extract category from ID prefix
        if "_" in gs.id:
            prefix = gs.id.split("_")[0]
        else:
            prefix = "OTHER"

        # Map common prefixes to readable names
        category_map = {
            "HALLMARK": "Hallmark",
            "KEGG": "KEGG Pathway",
            "REACTOME": "Reactome Pathway",
            "BIOCARTA": "BioCarta Pathway",
            "PID": "PID Pathway",
            "GO": "Gene Ontology",
            "HP": "Human Phenotype",
        }
        category = category_map.get(prefix, prefix)

        if category not in categories:
            categories[category] = {}
        categories[category][gs.id] = gs

    # Build collections
    return {
        name: GeneSetCollection(name=name, gene_sets=sets)
        for name, sets in categories.items()
    }
