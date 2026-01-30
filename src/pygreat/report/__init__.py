"""HTML report generation for GREAT enrichment results.

This module provides functionality to generate self-contained interactive
HTML reports from GREAT enrichment analysis results.

Example:
    >>> from pygreat.report import generate_report
    >>> generate_report("results.tsv", "report.html", title="My Analysis")

    >>> from pygreat.report import ReportGenerator, ReportConfig
    >>> config = ReportConfig(title="My Analysis", default_fdr=0.01)
    >>> generator = ReportGenerator(config)
    >>> generator.generate("results.tsv", "report.html")
"""

from pygreat.report.generator import ReportConfig, ReportGenerator, generate_report

__all__ = [
    "ReportConfig",
    "ReportGenerator",
    "generate_report",
]
