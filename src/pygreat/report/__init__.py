"""HTML report generation for GREAT enrichment results.

This module provides functionality to generate self-contained interactive
HTML reports from GREAT enrichment analysis results.

Example:
    Single-run report:
        >>> from pygreat.report import generate_report
        >>> generate_report("results.tsv", "report.html", title="My Analysis")

        >>> from pygreat.report import ReportGenerator, ReportConfig
        >>> config = ReportConfig(title="My Analysis", default_fdr=0.01)
        >>> generator = ReportGenerator(config)
        >>> generator.generate("results.tsv", "report.html")

    Multi-run comparison report:
        >>> from pygreat.report import generate_compare_report
        >>> generate_compare_report(
        ...     ["results_a.tsv", "results_b.tsv"],
        ...     "compare.html",
        ...     labels=["Treatment", "Control"],
        ... )

        >>> from pygreat.report import CompareReportGenerator, CompareReportConfig
        >>> config = CompareReportConfig(title="My Comparison", run_labels=["A", "B"])
        >>> generator = CompareReportGenerator(config)
        >>> generator.generate(["results_a.tsv", "results_b.tsv"], "compare.html")
"""

from pygreat.report.generator import (
    CompareReportConfig,
    CompareReportGenerator,
    ReportConfig,
    ReportGenerator,
    generate_compare_report,
    generate_report,
)

__all__ = [
    # Single-run report
    "ReportConfig",
    "ReportGenerator",
    "generate_report",
    # Multi-run comparison report
    "CompareReportConfig",
    "CompareReportGenerator",
    "generate_compare_report",
]
