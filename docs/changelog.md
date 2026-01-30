# Changelog

All notable changes to pygreat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-01-30

### Added

- **Local GREAT Analysis** - Run enrichment analysis locally without requiring the GREAT web service
  - `LocalGREAT` class for offline analysis with custom gene sets
  - Support for GTF gene annotations and GMT gene set files
  - Basal-plus-extension regulatory domain assignment
  - Both binomial and hypergeometric statistical tests
  - `pygreat local` CLI command for local analysis
- **Interactive HTML Reports** - Generate self-contained interactive reports from enrichment results
  - `pygreat report` CLI command to create HTML reports
  - Summary panel with total/significant terms per ontology
  - Interactive DataTables with search, sort, and pagination
  - Global filters for FDR, p-value thresholds, and top N terms
  - Term detail modal with stats, gene lists, and GO links (AmiGO, QuickGO)
  - Built-in plot builder for bar and dot plots with Plotly
  - Export options: SVG, PNG, TSV, CSV
  - Single self-contained HTML file (no external dependencies at runtime)
- `ReportGenerator` and `ReportConfig` classes for programmatic report generation
- `DataProcessor` class for loading and validating enrichment results

### Fixed

- Gene name/ID mismatch in local analysis - GMT files using gene symbols now correctly match GTF annotations using gene IDs

### Technical Details

- HTML reports use CDN-loaded libraries: Bootstrap 5, DataTables, jQuery, Plotly
- No new Python dependencies for report generation (uses existing pandas, json)
- Report module: `pygreat.report`

## [0.1.0] - 2026-01-24

### Added

- Initial release of pygreat
- `GreatClient` for submitting jobs to GREAT
- Support for multiple input formats:
  - Local BED files
  - URLs to public BED files (no upload needed)
  - pandas DataFrames
  - `GenomicRegions` objects
- Batch API integration for fast results
- `GreatJob` class for accessing enrichment results
- Filtering by FDR threshold and gene count
- Export to TSV and DataFrame formats
- Visualization functions:
  - `plot_enrichment_bar` - horizontal bar plots
  - `plot_enrichment_dot` - dot plots with size and color encoding
- Command-line interface with rich-click:
  - `pygreat submit` - submit jobs and save results
  - `pygreat plot` - create visualizations
- Support for GREAT v4.0.4:
  - Species: hg38, hg19, mm10, mm9
  - Association rules: basalPlusExt, twoClosest, oneClosest
- Background region support for foreground/background analysis
- Automatic rate limit handling with exponential backoff
- Full type hints and py.typed marker
- Comprehensive documentation

### Technical Details

- Uses GREAT batch API (`outputType=batch`) for direct TSV responses
- File hosting via transfer.sh for local file uploads
- HTTP client built on httpx
- Minimum Python version: 3.10

---

## Version History Format

### Types of Changes

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes
