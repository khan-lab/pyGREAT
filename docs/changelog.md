# Changelog

All notable changes to pygreat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-01-XX

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
