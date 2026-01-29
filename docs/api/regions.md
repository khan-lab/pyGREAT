# GenomicRegions

::: pygreat.models.regions.GenomicRegions
    options:
      show_source: false

## Overview

`GenomicRegions` represents a collection of genomic intervals. It handles parsing BED files, DataFrames, and provides methods for exporting regions in various formats.

## Creating GenomicRegions

### From BED File

```python
from pygreat.models import GenomicRegions

# From file path
regions = GenomicRegions.from_bed("peaks.bed")

# With explicit coordinate system
regions = GenomicRegions.from_bed("peaks.bed", zero_based=True)
```

### From DataFrame

```python
import pandas as pd
from pygreat.models import GenomicRegions

df = pd.DataFrame({
    "chrom": ["chr1", "chr1", "chr2"],
    "start": [1000, 5000, 10000],
    "end": [2000, 6000, 11000],
    "name": ["peak1", "peak2", "peak3"],  # Optional
})

regions = GenomicRegions.from_dataframe(df)
```

### From Lists

```python
from pygreat.models import GenomicRegions

regions = GenomicRegions(
    chromosomes=["chr1", "chr1", "chr2"],
    starts=[1000, 5000, 10000],
    ends=[2000, 6000, 11000],
    names=["peak1", "peak2", "peak3"],  # Optional
)
```

## Class Methods

### from_bed

Parse a BED file into GenomicRegions.

```python
@classmethod
def from_bed(
    cls,
    path: str | Path,
    zero_based: bool = True,
) -> GenomicRegions
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str \| Path` | Required | Path to BED file |
| `zero_based` | `bool` | `True` | Whether coordinates are 0-based |

### from_dataframe

Create GenomicRegions from a pandas DataFrame.

```python
@classmethod
def from_dataframe(
    cls,
    df: pd.DataFrame,
    zero_based: bool = True,
) -> GenomicRegions
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | `DataFrame` | Required | DataFrame with region columns |
| `zero_based` | `bool` | `True` | Whether coordinates are 0-based |

#### Recognized Column Names

The DataFrame must have columns for chromosome, start, and end. pygreat recognizes these variations:

| Field | Recognized Names |
|-------|------------------|
| Chromosome | `chrom`, `chr`, `chromosome`, `seqnames`, `Chromosome` |
| Start | `start`, `chromStart`, `txStart`, `Start` |
| End | `end`, `chromEnd`, `txEnd`, `End` |
| Name | `name`, `Name`, `id`, `ID` |

## Instance Methods

### to_bed

Export regions as BED format.

```python
def to_bed(self, gzip_compress: bool = False) -> bytes
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gzip_compress` | `bool` | `False` | Whether to gzip compress the output |

#### Returns

`bytes` - BED content as bytes.

#### Example

```python
# Plain BED
bed_content = regions.to_bed()

# Gzipped
bed_gz = regions.to_bed(gzip_compress=True)

# Save to file
with open("output.bed", "wb") as f:
    f.write(regions.to_bed())
```

### to_dataframe

Convert to a pandas DataFrame.

```python
def to_dataframe(self) -> pd.DataFrame
```

#### Returns

`DataFrame` - DataFrame with chrom, start, end, and name columns.

#### Example

```python
df = regions.to_dataframe()
print(df)
#   chrom  start    end   name
# 0  chr1   1000   2000  peak1
# 1  chr1   5000   6000  peak2
# 2  chr2  10000  11000  peak3
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `chromosomes` | `list[str]` | List of chromosome names |
| `starts` | `list[int]` | List of start positions |
| `ends` | `list[int]` | List of end positions |
| `names` | `list[str]` | List of region names |

## Iteration

GenomicRegions supports iteration:

```python
for chrom, start, end, name in regions:
    print(f"{chrom}:{start}-{end} ({name})")
```

## Length

Get the number of regions:

```python
n_regions = len(regions)
```

## Example: Filtering Regions

```python
from pygreat.models import GenomicRegions

# Load regions
regions = GenomicRegions.from_bed("peaks.bed")

# Convert to DataFrame for filtering
df = regions.to_dataframe()

# Filter to specific chromosome
chr1_df = df[df["chrom"] == "chr1"]

# Create new GenomicRegions from filtered DataFrame
chr1_regions = GenomicRegions.from_dataframe(chr1_df)
```

## Example: Merging Regions

```python
import pandas as pd
from pygreat.models import GenomicRegions

# Load two region sets
regions1 = GenomicRegions.from_bed("peaks1.bed")
regions2 = GenomicRegions.from_bed("peaks2.bed")

# Merge using DataFrames
df = pd.concat([
    regions1.to_dataframe(),
    regions2.to_dataframe(),
], ignore_index=True)

# Remove duplicates
df = df.drop_duplicates(subset=["chrom", "start", "end"])

# Create merged GenomicRegions
merged = GenomicRegions.from_dataframe(df)
```
