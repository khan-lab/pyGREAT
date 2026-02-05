"""Data processing for multi-run comparison reports.

Handles loading multiple enrichment result files, merging terms across runs,
computing shared/unique sets, and converting to JSON for the HTML report.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import pandas as pd

from pygreat.report.data_processor import DataProcessor


@dataclass
class RunData:
    """Data for a single run."""

    label: str
    df: pd.DataFrame
    summary: dict[str, Any]


@dataclass
class MergedTerm:
    """A term matched across multiple runs."""

    term_key: tuple[str, str]  # (category, term_id or normalized_name)
    term_id: str
    term_name: str
    category: str
    stats: dict[str, dict[str, Any] | None]  # {run_label: {fdr, p, fold, rank, ...}}
    presence: list[str]  # Run labels where term is present


@dataclass
class CompareData:
    """Complete comparison data structure."""

    runs: dict[str, RunData]
    run_labels: list[str]
    merged_terms: list[MergedTerm]
    shared_significant: list[tuple[str, str]]  # term_keys significant in ALL runs
    any_significant: list[tuple[str, str]]  # term_keys significant in ANY run
    unique_per_run: dict[str, list[tuple[str, str]]]  # {run_label: [term_keys]}
    categories: list[str]


class CompareDataProcessor:
    """Process and merge multiple enrichment result files for comparison."""

    def __init__(
        self,
        match_by: Literal["go_id", "term_name"] = "go_id",
        fdr_threshold: float = 0.05,
    ) -> None:
        """Initialize the compare processor.

        Args:
            match_by: How to match terms across runs ('go_id' or 'term_name').
            fdr_threshold: FDR threshold for significance.
        """
        self.match_by = match_by
        self.fdr_threshold = fdr_threshold
        self.base_processor = DataProcessor()

    def load_runs(
        self,
        files: list[Path],
        labels: list[str] | None = None,
    ) -> dict[str, RunData]:
        """Load multiple result files into RunData objects.

        Args:
            files: List of paths to TSV/CSV result files.
            labels: Optional labels for each run. If None, inferred from filenames.

        Returns:
            Dictionary mapping labels to RunData objects.

        Raises:
            ValueError: If number of labels doesn't match files.
        """
        if labels is None:
            labels = [self._infer_label(f) for f in files]

        if len(labels) != len(files):
            raise ValueError(
                f"Number of labels ({len(labels)}) must match files ({len(files)})"
            )

        # Ensure unique labels
        labels = self._make_unique_labels(labels)

        runs: dict[str, RunData] = {}
        for file_path, label in zip(files, labels):
            df = self.base_processor.load(file_path)
            warnings = self.base_processor.validate(df)
            # Log warnings but continue
            for w in warnings:
                print(f"Warning [{label}]: {w}")
            df = self.base_processor.categorize(df)
            summary = self.base_processor.compute_summary(df)
            runs[label] = RunData(label=label, df=df, summary=summary)

        return runs

    def _infer_label(self, path: Path) -> str:
        """Infer label from filename."""
        # Remove extension and clean up
        stem = path.stem
        # Replace common separators with spaces and title case
        label = stem.replace("_", " ").replace("-", " ")
        # Capitalize first letter of each word
        return label.title()

    def _make_unique_labels(self, labels: list[str]) -> list[str]:
        """Ensure all labels are unique by adding suffixes if needed."""
        seen: dict[str, int] = {}
        unique: list[str] = []

        for label in labels:
            if label in seen:
                seen[label] += 1
                unique.append(f"{label} ({seen[label]})")
            else:
                seen[label] = 1
                unique.append(label)

        return unique

    def _get_term_key(self, row: pd.Series) -> tuple[str, str]:
        """Generate term key based on match_by setting.

        Args:
            row: DataFrame row containing term data.

        Returns:
            Tuple of (category, identifier) for matching.
        """
        category = str(row.get("category", "Other"))
        if self.match_by == "go_id":
            return (category, str(row["term_id"]))
        else:
            # Normalize term name for matching
            name = str(row["term_name"]).lower().strip()
            return (category, name)

    def merge_runs(self, runs: dict[str, RunData]) -> CompareData:
        """Merge multiple runs into a unified comparison structure.

        Args:
            runs: Dictionary of run labels to RunData objects.

        Returns:
            CompareData with merged terms and computed sets.
        """
        run_labels = list(runs.keys())

        # Build term index: term_key -> {run_label -> row_data}
        term_index: dict[tuple[str, str], dict[str, pd.Series]] = {}

        for label, run in runs.items():
            for _, row in run.df.iterrows():
                key = self._get_term_key(row)
                if key not in term_index:
                    term_index[key] = {}
                term_index[key][label] = row

        # Detect FDR column
        fdr_col = self._detect_fdr_column(runs)

        # Build merged terms
        merged_terms: list[MergedTerm] = []

        for term_key, run_rows in term_index.items():
            # Use first available row for term metadata
            first_row = next(iter(run_rows.values()))

            stats: dict[str, dict[str, Any] | None] = {}
            for label in run_labels:
                if label in run_rows:
                    row = run_rows[label]
                    stats[label] = self._extract_stats(row, fdr_col)
                else:
                    stats[label] = None  # Term not present in this run

            merged = MergedTerm(
                term_key=term_key,
                term_id=str(first_row["term_id"]),
                term_name=str(first_row["term_name"]),
                category=term_key[0],
                stats=stats,
                presence=[label for label in run_labels if stats[label] is not None],
            )
            merged_terms.append(merged)

        # Compute shared/unique sets
        shared_significant: list[tuple[str, str]] = []
        any_significant: list[tuple[str, str]] = []
        unique_per_run: dict[str, list[tuple[str, str]]] = {
            label: [] for label in run_labels
        }

        for term in merged_terms:
            is_sig = {
                label: (
                    term.stats[label] is not None
                    and term.stats[label].get("fdr", 1.0) < self.fdr_threshold
                )
                for label in run_labels
            }

            sig_runs = [label for label, sig in is_sig.items() if sig]

            if len(sig_runs) == len(run_labels):
                shared_significant.append(term.term_key)

            if len(sig_runs) > 0:
                any_significant.append(term.term_key)

            if len(sig_runs) == 1:
                unique_per_run[sig_runs[0]].append(term.term_key)

        # Get all categories
        categories = sorted(set(t.category for t in merged_terms))

        return CompareData(
            runs=runs,
            run_labels=run_labels,
            merged_terms=merged_terms,
            shared_significant=shared_significant,
            any_significant=any_significant,
            unique_per_run=unique_per_run,
            categories=categories,
        )

    def _detect_fdr_column(self, runs: dict[str, RunData]) -> str:
        """Detect which FDR column to use across runs."""
        for run in runs.values():
            for col in ["binom_fdr", "hyper_fdr", "fdr", "q_value", "padj"]:
                if col in run.df.columns:
                    return col
        return "binom_fdr"  # Default

    def _detect_p_column(self, runs: dict[str, RunData]) -> str:
        """Detect which p-value column to use across runs."""
        for run in runs.values():
            for col in ["binom_p", "hyper_p", "p_value", "pvalue"]:
                if col in run.df.columns:
                    return col
        return "binom_p"  # Default

    def _extract_stats(self, row: pd.Series, fdr_col: str) -> dict[str, Any]:
        """Extract statistics from a row.

        Args:
            row: DataFrame row.
            fdr_col: Name of FDR column.

        Returns:
            Dictionary of statistics.
        """
        def safe_float(val: Any, default: float = 1.0) -> float:
            if pd.isna(val):
                return default
            try:
                return float(val)
            except (ValueError, TypeError):
                return default

        def safe_int(val: Any, default: int = 0) -> int:
            if pd.isna(val):
                return default
            try:
                return int(float(val))
            except (ValueError, TypeError):
                return default

        stats = {
            "fdr": safe_float(row.get(fdr_col), 1.0),
            "p": safe_float(
                row.get("binom_p", row.get("hyper_p", row.get("p_value"))), 1.0
            ),
            "fold": safe_float(
                row.get(
                    "binom_fold_enrichment",
                    row.get("hyper_fold_enrichment", row.get("fold_enrichment")),
                ),
                0.0,
            ),
            "observed_genes": safe_int(row.get("observed_genes"), 0),
            "expected_genes": safe_float(row.get("expected_genes"), 0.0),
            "total_genes": safe_int(row.get("total_genes"), 0),
            "rank": safe_int(
                row.get("binom_rank", row.get("hyper_rank", row.get("rank"))), 0
            ),
        }
        return stats

    def to_json(self, data: CompareData) -> str:
        """Convert CompareData to JSON for JavaScript consumption.

        Args:
            data: CompareData object to convert.

        Returns:
            JSON string.
        """
        output: dict[str, Any] = {
            "runLabels": data.run_labels,
            "runs": {},
            "merged": {
                "terms": [],
                "sharedSignificant": [
                    f"{k[0]}|{k[1]}" for k in data.shared_significant
                ],
                "anySignificant": [f"{k[0]}|{k[1]}" for k in data.any_significant],
                "uniquePerRun": {
                    label: [f"{k[0]}|{k[1]}" for k in keys]
                    for label, keys in data.unique_per_run.items()
                },
            },
            "categories": data.categories,
        }

        # Per-run data (for individual run tabs)
        for label, run in data.runs.items():
            # Get the JSON structure from base processor
            run_json = json.loads(self.base_processor.to_json(run.df))
            output["runs"][label] = {
                "summary": run.summary,
                "tables": run_json["tables"],
                "columns": run_json["columns"],
                "categories": run_json["categories"],
            }

        # Merged terms with computed fields
        for term in data.merged_terms:
            # Compute derived values
            fdr_values = [
                term.stats[label]["fdr"]
                for label in data.run_labels
                if term.stats[label] is not None
            ]

            neg_log_values = [
                -1 * _safe_log10(v) for v in fdr_values if v is not None and v > 0
            ]

            max_neg_log = max(neg_log_values) if neg_log_values else 0
            min_neg_log = min(neg_log_values) if neg_log_values else 0
            range_neg_log = max_neg_log - min_neg_log if neg_log_values else 0

            term_data = {
                "termKey": f"{term.term_key[0]}|{term.term_key[1]}",
                "termId": term.term_id,
                "termName": term.term_name,
                "category": term.category,
                "stats": term.stats,
                "presence": term.presence,
                "maxNegLog": round(max_neg_log, 4),
                "minNegLog": round(min_neg_log, 4),
                "range": round(range_neg_log, 4),
            }
            output["merged"]["terms"].append(term_data)

        return json.dumps(output, indent=None)


def _safe_log10(value: float) -> float:
    """Safely compute log10, handling zero and negative values."""
    import math

    if value <= 0:
        return 300  # -log10(1e-300)
    return math.log10(value)
