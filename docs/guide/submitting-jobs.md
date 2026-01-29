# Submitting Jobs

This guide covers all the ways to submit genomic regions to GREAT using pygreat.

## Input Formats

pygreat accepts genomic regions in several formats:

### Local BED File

```python
from pygreat import GreatClient

client = GreatClient()

# String path
job = client.submit_job("peaks.bed", species="hg38")

# Path object
from pathlib import Path
job = client.submit_job(Path("peaks.bed"), species="hg38")
```

### URL to Public BED File

If your BED file is publicly accessible, pass the URL directly. This skips the file upload step:

```python
job = client.submit_job(
    "https://example.com/data/peaks.bed",
    species="hg38",
)
```

!!! tip "URL Support"
    Using URLs is faster since pygreat doesn't need to upload your file to a hosting service first.

### pandas DataFrame

```python
import pandas as pd

regions = pd.DataFrame({
    "chrom": ["chr1", "chr1", "chr2"],
    "start": [1000, 5000, 10000],
    "end": [2000, 6000, 11000],
})

job = client.submit_job(regions, species="hg38")
```

The DataFrame must have columns for chromosome, start, and end positions. pygreat recognizes common column names:

- Chromosome: `chrom`, `chr`, `chromosome`, `seqnames`
- Start: `start`, `chromStart`, `txStart`
- End: `end`, `chromEnd`, `txEnd`

### GenomicRegions Object

For more control, use the `GenomicRegions` class directly:

```python
from pygreat.models import GenomicRegions

regions = GenomicRegions.from_bed("peaks.bed")
job = client.submit_job(regions, species="hg38")
```

## Supported Species

GREAT v4.0.4 supports these genome assemblies:

| Species | Assembly | Description |
|---------|----------|-------------|
| Human | `hg38` | GRCh38 (latest) |
| Human | `hg19` | GRCh37 |
| Mouse | `mm10` | GRCm38 |
| Mouse | `mm9` | NCBI37 |

```python
# Human (GRCh38)
job = client.submit_job("peaks.bed", species="hg38")

# Mouse
job = client.submit_job("peaks.bed", species="mm10")
```

## Association Rules

GREAT uses association rules to link genomic regions to genes. Three rules are available:

### Basal Plus Extension (Default)

The `basalPlusExt` rule defines:
- Basal domain: 5kb upstream, 1kb downstream of TSS
- Extension: Up to 1Mb in both directions until another gene's basal domain

```python
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    rule="basalPlusExt",  # Default
)
```

### Two Closest Genes

The `twoClosest` rule extends each region to the two nearest genes' TSS (up to 1Mb):

```python
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    rule="twoClosest",
)
```

### One Closest Gene

The `oneClosest` rule extends each region to the single nearest gene's TSS:

```python
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    rule="oneClosest",
)
```

## Background Regions

By default, GREAT uses the whole genome as background. For foreground/background analysis, provide background regions:

```python
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    background="background.bed",  # Background regions
)
```

Background can also be a URL or DataFrame:

```python
# URL
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    background="https://example.com/background.bed",
)

# DataFrame
bg_df = pd.DataFrame({
    "chrom": ["chr1", "chr2", "chr3"],
    "start": [0, 0, 0],
    "end": [10000000, 10000000, 10000000],
})
job = client.submit_job(regions_df, species="hg38", background=bg_df)
```

## Coordinate Systems

BED files use 0-based, half-open coordinates by default. If your input uses 1-based coordinates, set `zero_based=False`:

```python
# 0-based coordinates (BED standard)
job = client.submit_job("peaks.bed", species="hg38", zero_based=True)

# 1-based coordinates (e.g., from GFF)
job = client.submit_job("peaks.txt", species="hg38", zero_based=False)
```

## Job Naming

Optionally provide a job name for identification:

```python
job = client.submit_job(
    "peaks.bed",
    species="hg38",
    job_name="ChIP-seq_H3K4me3_sample1",
)
```

## Client Configuration

Configure the client for different scenarios:

```python
client = GreatClient(
    version="4.0.4",         # GREAT version
    request_interval=30.0,   # Seconds between retries
    max_retries=5,           # Max retry attempts
    timeout=300.0,           # Request timeout (seconds)
)
```

### Rate Limiting

GREAT limits concurrent requests. pygreat handles this with exponential backoff:

```python
# More patient retry settings
client = GreatClient(
    request_interval=60.0,  # Wait 60s between retries
    max_retries=10,         # Try up to 10 times
)
```

## Error Handling

Handle common errors:

```python
from pygreat import GreatClient
from pygreat.core.exceptions import (
    InvalidSpeciesError,
    RateLimitError,
    GreatError,
)

try:
    client = GreatClient()
    job = client.submit_job("peaks.bed", species="hg38")
except InvalidSpeciesError as e:
    print(f"Invalid species: {e}")
except RateLimitError as e:
    print(f"Rate limited, try again later: {e}")
except GreatError as e:
    print(f"GREAT error: {e}")
```
