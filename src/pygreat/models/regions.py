"""Genomic regions data model."""

from __future__ import annotations

import gzip
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

import pandas as pd

from pygreat.core.config import MAX_REGIONS
from pygreat.core.exceptions import InvalidRegionsError


@dataclass
class GenomicRegion:
    """A single genomic region.

    Attributes:
        chrom: Chromosome name (e.g., 'chr1').
        start: Start position (0-based).
        end: End position (exclusive).
        name: Optional region name.
        score: Optional score value.
        strand: Optional strand ('+' or '-').
    """

    chrom: str
    start: int
    end: int
    name: str | None = None
    score: float | None = None
    strand: str | None = None

    def to_bed_line(self) -> str:
        """Convert to BED format line.

        Returns:
            Tab-separated BED format string.
        """
        fields = [self.chrom, str(self.start), str(self.end)]
        if self.name is not None:
            fields.append(self.name)
            if self.score is not None:
                fields.append(str(self.score))
                if self.strand is not None:
                    fields.append(self.strand)
        return "\t".join(fields)


@dataclass
class GenomicRegions:
    """Collection of genomic regions.

    Provides conversion to/from various formats and validation.

    Attributes:
        regions: List of GenomicRegion objects.

    Example:
        >>> regions = GenomicRegions.from_bed("peaks.bed")
        >>> print(f"Loaded {len(regions)} regions")
        >>> bed_bytes = regions.to_bed(gzip_compress=True)
    """

    regions: list[GenomicRegion] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.regions)

    def __iter__(self) -> Iterator[GenomicRegion]:
        return iter(self.regions)

    def __getitem__(self, index: int) -> GenomicRegion:
        return self.regions[index]

    @classmethod
    def from_bed(
        cls,
        path: str | Path,
        zero_based: bool = True,
    ) -> GenomicRegions:
        """Load regions from a BED file.

        Args:
            path: Path to BED file (can be gzipped).
            zero_based: If True, coordinates are 0-based (BED standard).
                If False, start positions will be converted from 1-based.

        Returns:
            GenomicRegions instance.

        Raises:
            FileNotFoundError: If file does not exist.
            InvalidRegionsError: If regions are invalid.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"BED file not found: {path}")

        open_func = gzip.open if path.suffix == ".gz" else open
        regions = []

        with open_func(path, "rt") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines, comments, and track lines
                if not line or line.startswith("#") or line.startswith("track"):
                    continue
                if line.startswith("browser"):
                    continue

                fields = line.split("\t")
                if len(fields) < 3:
                    # Try splitting by any whitespace
                    fields = line.split()
                    if len(fields) < 3:
                        continue

                try:
                    start = int(fields[1])
                    if not zero_based:
                        start -= 1  # Convert to 0-based

                    region = GenomicRegion(
                        chrom=fields[0],
                        start=start,
                        end=int(fields[2]),
                        name=fields[3] if len(fields) > 3 else None,
                        score=float(fields[4]) if len(fields) > 4 else None,
                        strand=fields[5] if len(fields) > 5 else None,
                    )
                    regions.append(region)
                except (ValueError, IndexError) as e:
                    raise InvalidRegionsError(
                        f"Invalid BED format at line {line_num}: {line!r}"
                    ) from e

        instance = cls(regions=regions)
        instance.validate()
        return instance

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        zero_based: bool = True,
        chrom_col: str | None = None,
        start_col: str | None = None,
        end_col: str | None = None,
        name_col: str | None = None,
    ) -> GenomicRegions:
        """Create from pandas DataFrame.

        Automatically detects common column names if not specified.

        Args:
            df: DataFrame with chromosome, start, end columns.
            zero_based: If True, coordinates are 0-based.
            chrom_col: Name of chromosome column (auto-detected if None).
            start_col: Name of start position column (auto-detected if None).
            end_col: Name of end position column (auto-detected if None).
            name_col: Name of region name column (optional).

        Returns:
            GenomicRegions instance.

        Raises:
            InvalidRegionsError: If required columns not found.
        """
        # Auto-detect chromosome column
        if chrom_col is None:
            for col in ["chrom", "chr", "chromosome", "seqnames", "Chrom", "Chr"]:
                if col in df.columns:
                    chrom_col = col
                    break
            if chrom_col is None:
                raise InvalidRegionsError(
                    "Could not find chromosome column. "
                    "Expected one of: chrom, chr, chromosome, seqnames"
                )

        # Auto-detect start column
        if start_col is None:
            for col in ["start", "Start", "chromStart", "begin", "Begin"]:
                if col in df.columns:
                    start_col = col
                    break
            if start_col is None:
                raise InvalidRegionsError(
                    "Could not find start column. "
                    "Expected one of: start, Start, chromStart, begin"
                )

        # Auto-detect end column
        if end_col is None:
            for col in ["end", "End", "chromEnd", "stop", "Stop"]:
                if col in df.columns:
                    end_col = col
                    break
            if end_col is None:
                raise InvalidRegionsError(
                    "Could not find end column. "
                    "Expected one of: end, End, chromEnd, stop"
                )

        # Auto-detect name column
        if name_col is None:
            for col in ["name", "Name", "id", "ID", "region"]:
                if col in df.columns:
                    name_col = col
                    break

        regions = []
        for _, row in df.iterrows():
            start = int(row[start_col])
            if not zero_based:
                start -= 1

            name = None
            if name_col and name_col in df.columns:
                val = row[name_col]
                name = str(val) if pd.notna(val) else None

            region = GenomicRegion(
                chrom=str(row[chrom_col]),
                start=start,
                end=int(row[end_col]),
                name=name,
            )
            regions.append(region)

        instance = cls(regions=regions)
        instance.validate()
        return instance

    def to_bed(self, gzip_compress: bool = True) -> bytes:
        """Convert to BED format bytes.

        Args:
            gzip_compress: If True, return gzipped content.

        Returns:
            BED file content as bytes.
        """
        lines = [r.to_bed_line() for r in self.regions]
        content = "\n".join(lines) + "\n"

        if gzip_compress:
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                gz.write(content.encode("utf-8"))
            return buf.getvalue()

        return content.encode("utf-8")

    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame.

        Returns:
            DataFrame with columns: chrom, start, end, name, score, strand.
        """
        data = []
        for r in self.regions:
            data.append(
                {
                    "chrom": r.chrom,
                    "start": r.start,
                    "end": r.end,
                    "name": r.name,
                    "score": r.score,
                    "strand": r.strand,
                }
            )
        return pd.DataFrame(data)

    def validate(self) -> None:
        """Validate regions.

        Raises:
            InvalidRegionsError: If regions are invalid.
        """
        if len(self.regions) == 0:
            raise InvalidRegionsError("No regions provided")

        if len(self.regions) > MAX_REGIONS:
            raise InvalidRegionsError(
                f"Too many regions: {len(self.regions)} > {MAX_REGIONS}"
            )

        for i, r in enumerate(self.regions):
            if r.start < 0:
                raise InvalidRegionsError(
                    f"Region {i}: negative start coordinate {r.start}"
                )
            if r.end <= r.start:
                raise InvalidRegionsError(
                    f"Region {i}: end ({r.end}) must be > start ({r.start})"
                )
