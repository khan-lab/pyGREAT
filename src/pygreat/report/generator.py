"""HTML report generator for GREAT enrichment results.

Orchestrates the generation of self-contained interactive HTML reports
from enrichment analysis results.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from pygreat.report.data_processor import DataProcessor
from pygreat.report.template import CUSTOM_CSS, CUSTOM_JS, REPORT_TEMPLATE

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for HTML report generation.

    Attributes:
        title: Report title displayed in header.
        default_fdr: Default FDR threshold for filtering.
        default_top_n: Default number of top terms to display.
    """

    title: str = "GREAT Enrichment Report"
    default_fdr: float = 0.05
    default_top_n: int = 100


class ReportGenerator:
    """Generate interactive HTML reports from enrichment results.

    Example:
        >>> from pygreat.report import ReportGenerator, ReportConfig
        >>> config = ReportConfig(title="My Analysis")
        >>> generator = ReportGenerator(config)
        >>> generator.generate("results.tsv", "report.html")
    """

    def __init__(self, config: ReportConfig | None = None) -> None:
        """Initialize report generator.

        Args:
            config: Report configuration options.
        """
        self.config = config or ReportConfig()
        self.processor = DataProcessor()

    def generate(
        self,
        results: str | Path | pd.DataFrame,
        output: str | Path,
    ) -> Path:
        """Generate HTML report from enrichment results.

        Args:
            results: Path to TSV/CSV file or DataFrame with results.
            output: Path to write HTML report.

        Returns:
            Path to generated report file.

        Raises:
            FileNotFoundError: If results file doesn't exist.
            ValueError: If required columns are missing.
        """
        # Load data
        if isinstance(results, (str, Path)):
            df = self.processor.load(Path(results))
        else:
            df = results.copy()

        # Validate
        warnings = self.processor.validate(df)
        for warning in warnings:
            logger.warning(warning)

        # Categorize
        df = self.processor.categorize(df)

        # Compute summary
        summary = self.processor.compute_summary(df)

        # Convert to JSON for JavaScript
        data_json = self.processor.to_json(df)

        # Build HTML components
        summary_html = self._build_summary(summary)
        top_terms_html = self._build_top_terms(summary)
        filters_html = self._build_filters(summary)
        accordion_html = self._build_accordion(df)
        plot_builder_html = self._build_plot_builder()
        modal_html = self._build_modal()

        # Render template
        html = REPORT_TEMPLATE.format(
            title=self.config.title,
            custom_css=CUSTOM_CSS,
            summary_html=summary_html,
            top_terms_html=top_terms_html,
            filters_html=filters_html,
            accordion_html=accordion_html,
            plot_builder_html=plot_builder_html,
            modal_html=modal_html,
            data_json=data_json,
            config_json=json.dumps(asdict(self.config)),
            custom_js=CUSTOM_JS,
        )

        # Write output
        output_path = Path(output)
        output_path.write_text(html, encoding="utf-8")

        return output_path

    def _build_summary(self, summary: dict[str, Any]) -> str:
        """Build summary cards HTML.

        Args:
            summary: Summary statistics dictionary.

        Returns:
            HTML string for summary cards.
        """
        total = summary.get("total_terms", 0)
        significant = summary.get("significant_terms", 0)
        num_categories = len(summary.get("categories", {}))

        html = f"""
        <div class="summary-cards">
            <div class="summary-card">
                <div class="card-value">{total}</div>
                <div class="card-label">Total Terms</div>
            </div>
            <div class="summary-card significant">
                <div class="card-value">{significant}</div>
                <div class="card-label">Significant (FDR &lt; 0.05)</div>
            </div>
            <div class="summary-card">
                <div class="card-value">{num_categories}</div>
                <div class="card-label">Categories</div>
            </div>
        </div>
        """
        return html

    def _build_top_terms(self, summary: dict[str, Any]) -> str:
        """Build top terms section HTML.

        Args:
            summary: Summary statistics dictionary.

        Returns:
            HTML string for top terms section.
        """
        categories = summary.get("categories", {})

        if not categories:
            return ""

        category_html_parts = []
        for cat_name, cat_data in sorted(categories.items()):
            top_terms = cat_data.get("top_terms", [])
            if not top_terms:
                continue

            terms_html = ""
            for term in top_terms[:5]:
                fdr = term.get("fdr")
                fdr_str = f" <span class='fdr-badge'>(FDR: {fdr:.2e})</span>" if fdr else ""
                term_name = self._escape_html(term.get("term_name", ""))
                terms_html += f"<li>{term_name}{fdr_str}</li>"

            category_html_parts.append(f"""
                <div class="top-terms-category">
                    <h6>{self._escape_html(cat_name)} <span class="badge bg-secondary">{cat_data.get('total', 0)}</span></h6>
                    <ul>{terms_html}</ul>
                </div>
            """)

        if not category_html_parts:
            return ""

        return f"""
        <div class="top-terms-section">
            <h5 class="mb-3">Top Terms by Category</h5>
            <div class="top-terms-grid">
                {"".join(category_html_parts)}
            </div>
        </div>
        """

    def _build_filters(self, summary: dict[str, Any]) -> str:
        """Build filters bar HTML.

        Args:
            summary: Summary statistics dictionary.

        Returns:
            HTML string for filters bar.
        """
        categories = summary.get("categories", {})

        # Build category options
        category_options = '<option value="all">All Categories</option>'
        for cat_name in sorted(categories.keys()):
            category_options += f'<option value="{self._escape_html(cat_name)}">{self._escape_html(cat_name)}</option>'

        html = f"""
        <div class="filters-bar">
            <div class="filter-group">
                <label for="globalSearch">Search:</label>
                <input type="text" id="globalSearch" class="form-control form-control-sm"
                       placeholder="Search all terms...">
            </div>
            <div class="filter-group">
                <label for="categoryFilter">Category:</label>
                <select id="categoryFilter" class="form-select form-select-sm">
                    {category_options}
                </select>
            </div>
            <div class="filter-group">
                <label for="fdrFilter">Max FDR:</label>
                <select id="fdrFilter" class="form-select form-select-sm">
                    <option value="1">All</option>
                    <option value="0.05" selected>≤ 0.05</option>
                    <option value="0.01">≤ 0.01</option>
                    <option value="0.001">≤ 0.001</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="pvalFilter">Max P-value:</label>
                <select id="pvalFilter" class="form-select form-select-sm">
                    <option value="1" selected>All</option>
                    <option value="0.001">≤ 1e-3</option>
                    <option value="0.00001">≤ 1e-5</option>
                </select>
            </div>
            <div class="filter-group">
                <label for="topNFilter">Top N:</label>
                <select id="topNFilter" class="form-select form-select-sm">
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="20">20</option>
                    <option value="30">30</option>
                    <option value="100">100</option>
                    <option value="" selected>All</option>
                </select>
            </div>
        </div>
        """
        return html

    def _build_accordion(self, df: pd.DataFrame) -> str:
        """Build accordion sections HTML for each category.

        Args:
            df: DataFrame with 'category' column.

        Returns:
            HTML string for accordion.
        """
        categories = sorted(df["category"].unique())
        accordion_items = []

        for i, category in enumerate(categories):
            cat_df = df[df["category"] == category]
            count = len(cat_df)

            # Create safe ID
            cat_id = f"cat_{i}"

            # Determine if first item should be expanded
            show_class = "show" if i == 0 else ""
            collapsed_class = "" if i == 0 else "collapsed"

            accordion_items.append(f"""
            <div class="accordion-item" data-category="{self._escape_html(category)}">
                <h2 class="accordion-header">
                    <button class="accordion-button {collapsed_class}" type="button"
                            data-bs-toggle="collapse" data-bs-target="#{cat_id}"
                            data-category="{self._escape_html(category)}">
                        {self._escape_html(category)}
                        <span class="badge category-badge ms-2">{count}</span>
                    </button>
                </h2>
                <div id="{cat_id}" class="accordion-collapse collapse {show_class}"
                     data-bs-parent="#ontologyAccordion">
                    <div class="accordion-body table-container">
                        <table class="table table-striped table-hover enrichment-table"
                               data-category="{self._escape_html(category)}" style="width:100%">
                            <thead></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
            """)

        return f"""
        <div class="accordion" id="ontologyAccordion">
            {"".join(accordion_items)}
        </div>
        """

    def _build_plot_builder(self) -> str:
        """Build plot builder panel HTML.

        Returns:
            HTML string for plot builder.
        """
        return """
        <div class="card plot-builder">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span>Plot Builder</span>
                <div>
                    <button class="btn btn-sm btn-outline-secondary me-2" onclick="selectAllVisible()">
                        Select All Visible
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="deselectAll()">
                        Deselect All
                    </button>
                </div>
            </div>
            <div class="card-body">
                <p class="text-muted mb-3">
                    <span id="selectedCount">0</span> terms selected.
                    Select terms using checkboxes in the tables above.
                </p>

                <div class="plot-settings">
                    <div class="form-group">
                        <label for="plotType">Plot Type</label>
                        <select id="plotType" class="form-select form-select-sm">
                            <option value="bar">Bar Plot</option>
                            <option value="dot">Dot Plot</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="plotMetric">Metric</label>
                        <select id="plotMetric" class="form-select form-select-sm">
                            <option value="neglog_fdr">-log₁₀(FDR)</option>
                            <option value="neglog_p">-log₁₀(P-value)</option>
                            <option value="fold">Fold Enrichment</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="plotWidth">Width (px)</label>
                        <input type="number" id="plotWidth" class="form-control form-control-sm"
                               value="800" min="400" max="1600">
                    </div>
                    <div class="form-group">
                        <label for="plotHeight">Height (px)</label>
                        <input type="number" id="plotHeight" class="form-control form-control-sm"
                               value="600" min="300" max="1200">
                    </div>
                    <div class="form-group">
                        <label for="fontSize">Font Size</label>
                        <input type="number" id="fontSize" class="form-control form-control-sm"
                               value="12" min="8" max="20">
                    </div>
                    <div class="form-group">
                        <label for="colorPalette">Color Palette</label>
                        <select id="colorPalette" class="form-select form-select-sm">
                            <option value="Viridis">Viridis</option>
                            <option value="Blues">Blues</option>
                            <option value="Reds">Reds</option>
                            <option value="YlOrRd">Yellow-Orange-Red</option>
                            <option value="RdBu">Red-Blue</option>
                            <option value="Plasma">Plasma</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="orientation">Orientation</label>
                        <select id="orientation" class="form-select form-select-sm">
                            <option value="horizontal">Horizontal</option>
                            <option value="vertical">Vertical</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>&nbsp;</label>
                        <div class="form-check">
                            <input type="checkbox" id="showValues" class="form-check-input">
                            <label for="showValues" class="form-check-label">Show Values</label>
                        </div>
                    </div>
                </div>

                <button id="generatePlotBtn" class="btn btn-primary" onclick="generatePlot()" disabled>
                    Generate Plot
                </button>

                <div id="plotContainer" class="mt-3">
                    Select terms and click "Generate Plot" to create a visualization.
                </div>

                <div class="export-buttons">
                    <button class="btn btn-sm btn-outline-primary export-btn" onclick="exportSVG()" disabled>
                        Download SVG
                    </button>
                    <button class="btn btn-sm btn-outline-primary export-btn" onclick="exportPNG()" disabled>
                        Download PNG
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="exportSelectedTSV()">
                        Download Selected (TSV)
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="exportFilteredCSV()">
                        Download Filtered (CSV)
                    </button>
                </div>
            </div>
        </div>
        """

    def _build_modal(self) -> str:
        """Build term detail modal HTML.

        Returns:
            HTML string for modal.
        """
        return """
        <div class="modal fade" id="termModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="modalTermName">Term Name</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p><strong>Term ID:</strong> <span id="modalTermId"></span></p>

                        <h6 class="mt-3">Statistics</h6>
                        <div class="term-stats" id="modalStats">
                            <!-- Filled by JavaScript -->
                        </div>

                        <div id="genesSection" class="genes-section" style="display:none;">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <h6 class="mb-0">Associated Genes</h6>
                                <button id="copyGenesBtn" class="btn btn-sm btn-outline-secondary" onclick="copyGenes()">
                                    Copy Genes
                                </button>
                            </div>
                            <div class="genes-list" id="modalGenes"></div>
                        </div>

                        <div class="external-links mt-3">
                            <a id="amigoLink" href="#" target="_blank" class="btn btn-sm btn-outline-primary">
                                View in AmiGO
                            </a>
                            <a id="quickgoLink" href="#" target="_blank" class="btn btn-sm btn-outline-primary">
                                View in QuickGO
                            </a>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
        """

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: Text to escape.

        Returns:
            Escaped text safe for HTML.
        """
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )


def generate_report(
    results: str | Path | pd.DataFrame,
    output: str | Path,
    title: str = "GREAT Enrichment Report",
    default_fdr: float = 0.05,
    default_top_n: int = 100,
) -> Path:
    """Generate HTML report from enrichment results.

    Convenience function for quick report generation.

    Args:
        results: Path to TSV/CSV file or DataFrame with results.
        output: Path to write HTML report.
        title: Report title.
        default_fdr: Default FDR threshold.
        default_top_n: Default top N terms.

    Returns:
        Path to generated report file.

    Example:
        >>> from pygreat.report import generate_report
        >>> generate_report("results.tsv", "report.html", title="My Analysis")
    """
    config = ReportConfig(
        title=title,
        default_fdr=default_fdr,
        default_top_n=default_top_n,
    )
    generator = ReportGenerator(config)
    return generator.generate(results, output)
