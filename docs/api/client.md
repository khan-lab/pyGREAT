# GreatClient

::: pygreat.core.client.GreatClient
    options:
      show_source: false
      members:
        - __init__
        - submit_job
        - close
        - __enter__
        - __exit__

## Overview

`GreatClient` is the main entry point for interacting with the GREAT web service. It handles:

- Uploading genomic regions to a file hosting service (when needed)
- Calling the GREAT batch API
- Parsing responses into structured results
- Managing HTTP connections and rate limiting

## Basic Usage

```python
from pygreat import GreatClient

# Create client with default settings
client = GreatClient()

# Submit a job
job = client.submit_job("peaks.bed", species="hg38")

# Get results
results = job.get_enrichment_tables()

# Clean up
client.close()
```

## Context Manager

Use the context manager pattern for automatic cleanup:

```python
with GreatClient() as client:
    job = client.submit_job("peaks.bed", species="hg38")
    results = job.get_enrichment_tables()
# Client is automatically closed
```

## Constructor

```python
GreatClient(
    base_url: str | None = None,
    version: str = "4.0.4",
    request_interval: float = 30.0,
    max_retries: int = 5,
    timeout: float = 300.0,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str \| None` | `None` | Custom GREAT server URL. If None, uses the official Stanford server. |
| `version` | `str` | `"4.0.4"` | GREAT version to use. Affects supported species. |
| `request_interval` | `float` | `30.0` | Base seconds between retry attempts for rate limiting. |
| `max_retries` | `int` | `5` | Maximum number of retry attempts. |
| `timeout` | `float` | `300.0` | HTTP request timeout in seconds. |

## Methods

### submit_job

Submit genomic regions to GREAT for enrichment analysis.

```python
def submit_job(
    self,
    regions: str | Path | pd.DataFrame | GenomicRegions,
    species: Species = "hg38",
    *,
    background: str | Path | pd.DataFrame | GenomicRegions | None = None,
    rule: AssociationRule = "basalPlusExt",
    job_name: str | None = None,
    zero_based: bool = False,
) -> GreatJob
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `regions` | Various | Required | Input genomic regions. Accepts: BED file path, URL, DataFrame, or GenomicRegions |
| `species` | `str` | `"hg38"` | Genome assembly: `"hg38"`, `"hg19"`, `"mm10"`, or `"mm9"` |
| `background` | Various | `None` | Optional background regions for foreground/background analysis |
| `rule` | `str` | `"basalPlusExt"` | Association rule: `"basalPlusExt"`, `"twoClosest"`, or `"oneClosest"` |
| `job_name` | `str \| None` | `None` | Optional job identifier |
| `zero_based` | `bool` | `False` | Whether input coordinates are 0-based (BED standard) |

#### Returns

`GreatJob` - Object containing enrichment results and metadata.

#### Raises

| Exception | Condition |
|-----------|-----------|
| `InvalidSpeciesError` | Species not supported for the GREAT version |
| `RateLimitError` | Rate limit exceeded after max retries |
| `ConnectionError` | Network or server error |

#### Examples

```python
# From local file
job = client.submit_job("peaks.bed", species="hg38")

# From URL (no upload needed)
job = client.submit_job("https://example.com/peaks.bed", species="hg38")

# From DataFrame
import pandas as pd
df = pd.DataFrame({
    "chrom": ["chr1", "chr2"],
    "start": [1000, 2000],
    "end": [1500, 2500],
})
job = client.submit_job(df, species="hg38")

# With background
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    background="background.bed",
)

# With custom rule
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    rule="twoClosest",
)
```

### close

Close the HTTP client and release resources.

```python
def close(self) -> None
```

Always call `close()` when done, or use the context manager.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `base_url` | `str` | The GREAT server URL |
| `version` | `str` | GREAT version |
| `request_interval` | `float` | Base retry interval |
| `max_retries` | `int` | Maximum retries |
| `timeout` | `float` | Request timeout |

## Rate Limiting

GREAT limits concurrent requests globally (not per-user). pygreat handles rate limiting with exponential backoff:

1. If rate limited, wait `request_interval` seconds
2. On subsequent failures, double the wait time (up to 5 minutes)
3. Retry up to `max_retries` times

Configure for high-load scenarios:

```python
client = GreatClient(
    request_interval=60.0,  # Longer initial wait
    max_retries=10,         # More attempts
)
```

## Thread Safety

`GreatClient` is **not thread-safe**. For concurrent usage, create separate client instances per thread.
