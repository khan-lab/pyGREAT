"""Tests for GenomicRegions model."""

import gzip
from pathlib import Path

import pandas as pd
import pytest

from pygreat.core.exceptions import InvalidRegionsError
from pygreat.models.regions import GenomicRegion, GenomicRegions


class TestGenomicRegion:
    """Tests for GenomicRegion class."""

    def test_creation(self) -> None:
        """Test basic region creation."""
        region = GenomicRegion("chr1", 1000, 2000, "peak1")
        assert region.chrom == "chr1"
        assert region.start == 1000
        assert region.end == 2000
        assert region.name == "peak1"

    def test_to_bed_line_minimal(self) -> None:
        """Test BED line with minimal fields."""
        region = GenomicRegion("chr1", 1000, 2000)
        assert region.to_bed_line() == "chr1\t1000\t2000"

    def test_to_bed_line_with_name(self) -> None:
        """Test BED line with name."""
        region = GenomicRegion("chr1", 1000, 2000, "peak1")
        assert region.to_bed_line() == "chr1\t1000\t2000\tpeak1"

    def test_to_bed_line_full(self) -> None:
        """Test BED line with all fields."""
        region = GenomicRegion("chr1", 1000, 2000, "peak1", 100.0, "+")
        assert region.to_bed_line() == "chr1\t1000\t2000\tpeak1\t100.0\t+"


class TestGenomicRegions:
    """Tests for GenomicRegions class."""

    def test_from_bed(self, sample_bed_file: Path) -> None:
        """Test loading from BED file."""
        regions = GenomicRegions.from_bed(sample_bed_file)
        assert len(regions) == 5
        assert regions[0].chrom == "chr1"
        assert regions[0].start == 1000
        assert regions[0].end == 2000

    def test_from_bed_with_comments(self, tmp_path: Path) -> None:
        """Test loading BED file with comments."""
        bed_path = tmp_path / "test.bed"
        content = """# This is a comment
track name=test
browser position chr1:1000-2000
chr1\t1000\t2000\tpeak1
chr2\t5000\t6000\tpeak2
"""
        bed_path.write_text(content)
        regions = GenomicRegions.from_bed(bed_path)
        assert len(regions) == 2

    def test_from_dataframe(self, sample_dataframe: pd.DataFrame) -> None:
        """Test creating from DataFrame."""
        regions = GenomicRegions.from_dataframe(sample_dataframe)
        assert len(regions) == 5
        assert regions[0].chrom == "chr1"
        assert regions[0].name == "peak1"

    def test_from_dataframe_auto_detect_columns(self) -> None:
        """Test auto-detection of column names."""
        df = pd.DataFrame(
            {
                "chr": ["chr1", "chr2"],
                "Start": [100, 200],
                "End": [200, 300],
            }
        )
        regions = GenomicRegions.from_dataframe(df)
        assert len(regions) == 2
        assert regions[0].chrom == "chr1"

    def test_from_dataframe_missing_columns(self) -> None:
        """Test error on missing columns."""
        df = pd.DataFrame({"foo": [1, 2], "bar": [3, 4]})
        with pytest.raises(InvalidRegionsError, match="Could not find chromosome"):
            GenomicRegions.from_dataframe(df)

    def test_to_bed_uncompressed(self, sample_regions: GenomicRegions) -> None:
        """Test export to uncompressed BED."""
        content = sample_regions.to_bed(gzip_compress=False)
        assert isinstance(content, bytes)
        lines = content.decode().strip().split("\n")
        assert len(lines) == 5
        assert lines[0].startswith("chr1\t1000\t2000")

    def test_to_bed_gzipped(self, sample_regions: GenomicRegions) -> None:
        """Test export to gzipped BED."""
        content = sample_regions.to_bed(gzip_compress=True)
        assert isinstance(content, bytes)
        # Check gzip magic number
        assert content[:2] == b"\x1f\x8b"
        # Decompress and verify
        decompressed = gzip.decompress(content)
        lines = decompressed.decode().strip().split("\n")
        assert len(lines) == 5

    def test_to_dataframe(self, sample_regions: GenomicRegions) -> None:
        """Test conversion to DataFrame."""
        df = sample_regions.to_dataframe()
        assert len(df) == 5
        assert list(df.columns) == ["chrom", "start", "end", "name", "score", "strand"]
        assert df.iloc[0]["chrom"] == "chr1"

    def test_validation_empty(self) -> None:
        """Test validation of empty regions."""
        with pytest.raises(InvalidRegionsError, match="No regions"):
            GenomicRegions(regions=[]).validate()

    def test_validation_negative_start(self) -> None:
        """Test validation of negative start."""
        with pytest.raises(InvalidRegionsError, match="negative start"):
            GenomicRegions(regions=[GenomicRegion("chr1", -100, 200)]).validate()

    def test_validation_invalid_coordinates(self) -> None:
        """Test validation of end <= start."""
        with pytest.raises(InvalidRegionsError, match="end .* must be > start"):
            GenomicRegions(regions=[GenomicRegion("chr1", 200, 100)]).validate()

    def test_iteration(self, sample_regions: GenomicRegions) -> None:
        """Test iteration over regions."""
        chroms = [r.chrom for r in sample_regions]
        assert chroms == ["chr1", "chr1", "chr2", "chr3", "chr5"]

    def test_len(self, sample_regions: GenomicRegions) -> None:
        """Test length."""
        assert len(sample_regions) == 5

    def test_getitem(self, sample_regions: GenomicRegions) -> None:
        """Test indexing."""
        assert sample_regions[0].chrom == "chr1"
        assert sample_regions[-1].chrom == "chr5"
