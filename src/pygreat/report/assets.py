"""Embedded JavaScript and CSS libraries for offline reports.

This module provides library content for generating self-contained HTML reports
that work without internet access. It supports both CDN mode (external links)
and offline mode (embedded minified libraries).

The embedded libraries are loaded lazily from bundled files or downloaded
on first use when offline mode is requested.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

# Library versions
TABULATOR_VERSION = "5.5.2"
PLOTLY_VERSION = "2.27.0"
BOOTSTRAP_VERSION = "5.3.2"


class LibraryURLs(NamedTuple):
    """CDN URLs for JavaScript and CSS libraries."""

    # Tabulator (replaces DataTables + jQuery)
    tabulator_css: str = (
        f"https://unpkg.com/tabulator-tables@{TABULATOR_VERSION}/dist/css/"
        "tabulator_bootstrap5.min.css"
    )
    tabulator_js: str = (
        f"https://unpkg.com/tabulator-tables@{TABULATOR_VERSION}/dist/js/"
        "tabulator.min.js"
    )

    # Plotly (basic distribution - scatter, bar, heatmap)
    plotly_js: str = f"https://cdn.plot.ly/plotly-basic-{PLOTLY_VERSION}.min.js"

    # Bootstrap
    bootstrap_css: str = (
        f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/"
        "bootstrap.min.css"
    )
    bootstrap_js: str = (
        f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/"
        "bootstrap.bundle.min.js"
    )


# Default CDN URLs
CDN_URLS = LibraryURLs()


def get_cdn_css_links() -> str:
    """Get HTML link tags for CSS libraries from CDN.

    Returns:
        HTML string with link tags.
    """
    return f"""
    <link href="{CDN_URLS.bootstrap_css}" rel="stylesheet"
          integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN"
          crossorigin="anonymous">
    <link href="{CDN_URLS.tabulator_css}" rel="stylesheet">
    """


def get_cdn_js_scripts() -> str:
    """Get HTML script tags for JavaScript libraries from CDN.

    Returns:
        HTML string with script tags.
    """
    return f"""
    <script src="{CDN_URLS.bootstrap_js}"
            integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL"
            crossorigin="anonymous"></script>
    <script src="{CDN_URLS.tabulator_js}"></script>
    <script src="{CDN_URLS.plotly_js}"></script>
    """


def get_offline_css() -> str:
    """Get inline CSS for offline mode.

    Returns:
        HTML string with embedded CSS in style tags.
    """
    # Check if we have cached offline assets
    offline_css = _load_offline_asset("offline_css.min.css")
    if offline_css:
        return f"<style>{offline_css}</style>"

    # Fallback: return CDN links (will require internet)
    return get_cdn_css_links()


def get_offline_js() -> str:
    """Get inline JavaScript for offline mode.

    Returns:
        HTML string with embedded JS in script tags.
    """
    # Check if we have cached offline assets
    offline_js = _load_offline_asset("offline_js.min.js")
    if offline_js:
        return f"<script>{offline_js}</script>"

    # Fallback: return CDN scripts (will require internet)
    return get_cdn_js_scripts()


def _load_offline_asset(filename: str) -> str | None:
    """Load an offline asset file if it exists.

    Args:
        filename: Name of the asset file.

    Returns:
        Content of the file, or None if not found.
    """
    # Look for assets in the same directory as this module
    assets_dir = Path(__file__).parent / "offline_assets"
    asset_path = assets_dir / filename

    if asset_path.exists():
        return asset_path.read_text(encoding="utf-8")

    return None


def get_library_tags(offline: bool = True) -> tuple[str, str]:
    """Get CSS and JS library tags based on offline mode.

    Args:
        offline: If True, attempt to use embedded libraries.
                 Falls back to CDN if offline assets not available.

    Returns:
        Tuple of (css_html, js_html) strings.
    """
    if offline:
        css = get_offline_css()
        js = get_offline_js()
    else:
        css = get_cdn_css_links()
        js = get_cdn_js_scripts()

    return css, js


# Minimal inline CSS fallback for basic functionality
# This provides essential styling even without Bootstrap
MINIMAL_FALLBACK_CSS = """
<style>
/* Minimal fallback styles */
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       margin: 0; padding: 1rem; background: #f8fafc; color: #1e293b; }
.container-fluid { max-width: 1400px; margin: 0 auto; }
.card { background: white; border-radius: 0.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem; }
.card-header { padding: 0.75rem 1rem; border-bottom: 1px solid #e2e8f0; font-weight: 600; }
.card-body { padding: 1rem; }
.nav-tabs { display: flex; gap: 0.25rem; border-bottom: 2px solid #e2e8f0; margin-bottom: 1rem; }
.nav-link { padding: 0.5rem 1rem; text-decoration: none; color: #64748b; cursor: pointer;
            border-radius: 0.25rem 0.25rem 0 0; }
.nav-link:hover { background: #f1f5f9; }
.nav-link.active { background: #3b82f6; color: white; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; cursor: pointer;
       background: #3b82f6; color: white; }
.btn:hover { background: #2563eb; }
.btn-secondary { background: #64748b; }
.form-control, .form-select { padding: 0.375rem 0.75rem; border: 1px solid #d1d5db;
                              border-radius: 0.25rem; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.5rem; text-align: left; border-bottom: 1px solid #e2e8f0; }
th { background: #f8fafc; font-weight: 600; }
tr:hover { background: #f1f5f9; }
.row { display: flex; flex-wrap: wrap; gap: 1rem; }
.col-md-4 { flex: 0 0 calc(33.333% - 0.67rem); }
.col-md-6 { flex: 0 0 calc(50% - 0.5rem); }
.col-lg-8 { flex: 0 0 calc(66.667% - 0.33rem); }
@media (max-width: 768px) {
    .col-md-4, .col-md-6, .col-lg-8 { flex: 0 0 100%; }
}
</style>
"""


def ensure_offline_assets() -> bool:
    """Download and cache offline assets if not present.

    This function downloads the minified libraries from CDN and caches
    them locally for offline use.

    Returns:
        True if assets are available, False if download failed.
    """
    import urllib.request

    assets_dir = Path(__file__).parent / "offline_assets"
    assets_dir.mkdir(exist_ok=True)

    # Define what we need to download
    downloads = [
        (CDN_URLS.bootstrap_css, "bootstrap.min.css"),
        (CDN_URLS.bootstrap_js, "bootstrap.bundle.min.js"),
        (CDN_URLS.tabulator_css, "tabulator_bootstrap5.min.css"),
        (CDN_URLS.tabulator_js, "tabulator.min.js"),
        (CDN_URLS.plotly_js, "plotly-basic.min.js"),
    ]

    all_success = True
    for url, filename in downloads:
        filepath = assets_dir / filename
        if not filepath.exists():
            try:
                print(f"Downloading {filename}...")
                urllib.request.urlretrieve(url, filepath)
            except Exception as e:
                print(f"Failed to download {filename}: {e}")
                all_success = False

    # If we have all files, combine them
    if all_success:
        _combine_offline_assets(assets_dir)

    return all_success


def _combine_offline_assets(assets_dir: Path) -> None:
    """Combine downloaded assets into single CSS and JS files."""
    # Combine CSS
    css_files = ["bootstrap.min.css", "tabulator_bootstrap5.min.css"]
    css_content = []
    for f in css_files:
        filepath = assets_dir / f
        if filepath.exists():
            css_content.append(filepath.read_text(encoding="utf-8"))

    if css_content:
        combined_css = assets_dir / "offline_css.min.css"
        combined_css.write_text("\n".join(css_content), encoding="utf-8")

    # Combine JS
    js_files = ["bootstrap.bundle.min.js", "tabulator.min.js", "plotly-basic.min.js"]
    js_content = []
    for f in js_files:
        filepath = assets_dir / f
        if filepath.exists():
            js_content.append(filepath.read_text(encoding="utf-8"))

    if js_content:
        combined_js = assets_dir / "offline_js.min.js"
        combined_js.write_text("\n".join(js_content), encoding="utf-8")
