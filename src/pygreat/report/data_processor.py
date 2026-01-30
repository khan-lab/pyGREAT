"""Data processing for HTML report generation.

Handles loading, validation, categorization, and JSON conversion
of GREAT enrichment results for the interactive HTML report.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


class DataProcessor:
    """Process enrichment results for HTML report generation."""

    REQUIRED_COLS = ["term_id", "term_name"]
    STAT_COLS = ["binom_fdr", "binom_p", "hyper_fdr", "hyper_p"]
    OPTIONAL_COLS = [
        "ontology",
        "binom_rank",
        "binom_bonferroni",
        "binom_fold_enrichment",
        "hyper_rank",
        "hyper_bonferroni",
        "hyper_fold_enrichment",
        "observed_regions",
        "expected_regions",
        "observed_genes",
        "expected_genes",
        "total_genes",
        "genome_fraction",
        "genes",
        "regions",
    ]

    # GO category patterns
    GO_BP_PATTERNS = [
        r"biological.?process",
        r"\bBP\b",
        r"GO.?BP",
    ]
    GO_MF_PATTERNS = [
        r"molecular.?function",
        r"\bMF\b",
        r"GO.?MF",
    ]
    GO_CC_PATTERNS = [
        r"cellular.?component",
        r"\bCC\b",
        r"GO.?CC",
    ]

    def load(self, path: Path) -> pd.DataFrame:
        """Load enrichment results from TSV or CSV file.

        Args:
            path: Path to results file.

        Returns:
            DataFrame with enrichment results.

        Raises:
            FileNotFoundError: If file doesn't exist.
            ValueError: If file format is not supported.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Results file not found: {path}")

        suffix = path.suffix.lower()

        if suffix in (".tsv", ".txt"):
            df = pd.read_csv(path, sep="\t")
        elif suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix == ".json":
            df = pd.read_json(path)
        else:
            # Try to auto-detect
            with open(path) as f:
                first_line = f.readline()
            if "\t" in first_line:
                df = pd.read_csv(path, sep="\t")
            else:
                df = pd.read_csv(path)

        return df

    def validate(self, df: pd.DataFrame) -> list[str]:
        """Validate DataFrame and return warnings.

        Args:
            df: DataFrame to validate.

        Returns:
            List of warning messages.

        Raises:
            ValueError: If required columns are missing.
        """
        warnings: list[str] = []

        # Check required columns
        missing_required = [c for c in self.REQUIRED_COLS if c not in df.columns]
        if missing_required:
            raise ValueError(f"Missing required columns: {missing_required}")

        # Check for at least one stat column
        has_stat = any(c in df.columns for c in self.STAT_COLS)
        if not has_stat:
            warnings.append(
                f"No statistical columns found. Expected one of: {self.STAT_COLS}"
            )

        # Check for empty data
        if len(df) == 0:
            warnings.append("DataFrame is empty - no terms to display")

        # Check for missing values in key columns
        for col in self.REQUIRED_COLS:
            if df[col].isna().any():
                warnings.append(f"Column '{col}' contains missing values")

        return warnings

    def categorize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add category column based on ontology information.

        Categories: GO BP, GO MF, GO CC, Other

        Args:
            df: DataFrame with enrichment results.

        Returns:
            DataFrame with 'category' column added.
        """
        df = df.copy()

        def _get_category(row: pd.Series) -> str:
            # Check ontology column first
            ontology = str(row.get("ontology", "")).lower()
            term_id = str(row.get("term_id", ""))

            # Check for GO BP
            for pattern in self.GO_BP_PATTERNS:
                if re.search(pattern, ontology, re.IGNORECASE):
                    return "Biological Process"

            # Check for GO MF
            for pattern in self.GO_MF_PATTERNS:
                if re.search(pattern, ontology, re.IGNORECASE):
                    return "Molecular Function"

            # Check for GO CC
            for pattern in self.GO_CC_PATTERNS:
                if re.search(pattern, ontology, re.IGNORECASE):
                    return "Cellular Component"

            # If ontology just says "GO", try to infer from term_id
            # GO IDs have structure like GO:0008150
            if term_id.startswith("GO:"):
                # For now, if we can't determine, put in generic GO category
                if "go" in ontology.lower() and ontology.lower() not in ["go bp", "go mf", "go cc"]:
                    return "GO"

            # Check for other common ontologies
            if any(x in ontology for x in ["pathway", "kegg", "reactome", "msigdb"]):
                return "Pathway"
            if any(x in ontology for x in ["disease", "hpo", "omim"]):
                return "Disease"
            if any(x in ontology for x in ["regulatory", "encode", "tfbs"]):
                return "Regulatory"

            # Default to ontology name or "Other"
            if ontology and ontology != "nan":
                return ontology.title()

            return "Other"

        df["category"] = df.apply(_get_category, axis=1)
        return df

    def compute_summary(self, df: pd.DataFrame) -> dict[str, Any]:
        """Compute summary statistics for the report.

        Args:
            df: DataFrame with 'category' column.

        Returns:
            Dictionary with summary statistics.
        """
        summary: dict[str, Any] = {
            "total_terms": len(df),
            "categories": {},
        }

        # Determine FDR column
        fdr_col = None
        for col in ["binom_fdr", "hyper_fdr", "fdr", "q_value", "padj"]:
            if col in df.columns:
                fdr_col = col
                break

        # Count significant terms
        if fdr_col:
            significant = df[df[fdr_col] < 0.05]
            summary["significant_terms"] = len(significant)
            summary["fdr_column"] = fdr_col
        else:
            summary["significant_terms"] = 0
            summary["fdr_column"] = None

        # Per-category summary
        for category in df["category"].unique():
            cat_df = df[df["category"] == category]
            cat_summary = {
                "total": len(cat_df),
                "significant": 0,
                "top_terms": [],
            }

            if fdr_col:
                cat_significant = cat_df[cat_df[fdr_col] < 0.05]
                cat_summary["significant"] = len(cat_significant)

                # Top 5 terms by FDR
                top = cat_df.nsmallest(5, fdr_col)
                cat_summary["top_terms"] = [
                    {
                        "term_id": row["term_id"],
                        "term_name": row["term_name"],
                        "fdr": float(row[fdr_col]) if pd.notna(row[fdr_col]) else None,
                    }
                    for _, row in top.iterrows()
                ]

            summary["categories"][category] = cat_summary

        return summary

    def to_json(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to JSON for JavaScript consumption.

        Args:
            df: DataFrame with 'category' column.

        Returns:
            JSON string with tables grouped by category.
        """
        # Get all columns
        all_columns = list(df.columns)

        # Define column metadata for DataTables
        columns_meta = []
        for col in all_columns:
            if col == "category":
                continue  # Skip category column in table display

            col_meta: dict[str, Any] = {
                "data": col,
                "title": self._format_column_title(col),
            }

            # Add formatting hints
            if col in ["binom_p", "hyper_p", "binom_fdr", "hyper_fdr", "binom_bonferroni", "hyper_bonferroni"]:
                col_meta["type"] = "num"
                col_meta["render_type"] = "scientific"
            elif col in ["binom_fold_enrichment", "hyper_fold_enrichment", "genome_fraction"]:
                col_meta["type"] = "num"
                col_meta["render_type"] = "decimal"
            elif col in ["observed_regions", "expected_regions", "observed_genes", "expected_genes", "total_genes", "binom_rank", "hyper_rank"]:
                col_meta["type"] = "num"
                col_meta["render_type"] = "integer"

            columns_meta.append(col_meta)

        # Group data by category
        tables: dict[str, list[dict[str, Any]]] = {}
        for category in sorted(df["category"].unique()):
            cat_df = df[df["category"] == category]
            # Convert to list of dicts, handling NaN values
            records = []
            for _, row in cat_df.iterrows():
                record = {}
                for col in all_columns:
                    if col == "category":
                        continue
                    val = row[col]
                    if pd.isna(val):
                        record[col] = None
                    elif isinstance(val, float):
                        record[col] = val
                    else:
                        record[col] = str(val) if not isinstance(val, (int, bool)) else val
                records.append(record)
            tables[category] = records

        data = {
            "columns": columns_meta,
            "tables": tables,
            "categories": list(tables.keys()),
        }

        return json.dumps(data, indent=None)

    def _format_column_title(self, col: str) -> str:
        """Format column name for display.

        Args:
            col: Column name.

        Returns:
            Formatted title.
        """
        # Special formatting for known columns
        title_map = {
            "term_id": "Term ID",
            "term_name": "Term Name",
            "binom_p": "Binom P",
            "binom_fdr": "Binom FDR",
            "binom_fold_enrichment": "Binom Fold",
            "binom_rank": "Binom Rank",
            "binom_bonferroni": "Binom Bonf",
            "hyper_p": "Hyper P",
            "hyper_fdr": "Hyper FDR",
            "hyper_fold_enrichment": "Hyper Fold",
            "hyper_rank": "Hyper Rank",
            "hyper_bonferroni": "Hyper Bonf",
            "observed_regions": "Obs Regions",
            "expected_regions": "Exp Regions",
            "observed_genes": "Obs Genes",
            "expected_genes": "Exp Genes",
            "total_genes": "Total Genes",
            "genome_fraction": "Genome Frac",
            "ontology": "Ontology",
            "genes": "Genes",
            "regions": "Regions",
        }

        if col in title_map:
            return title_map[col]

        # Default: title case with underscores replaced
        return col.replace("_", " ").title()
