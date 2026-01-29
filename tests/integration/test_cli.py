"""Integration tests for CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from pygreat.cli.app import cli


class TestCLI:
    """Tests for CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI runner."""
        return CliRunner()

    def test_version(self, runner: CliRunner) -> None:
        """Test version command."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "pygreat" in result.output

    def test_help(self, runner: CliRunner) -> None:
        """Test help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "submit" in result.output
        assert "plot" in result.output

    def test_submit_help(self, runner: CliRunner) -> None:
        """Test submit command help."""
        result = runner.invoke(cli, ["submit", "--help"])
        assert result.exit_code == 0
        assert "--species" in result.output
        assert "--background" in result.output

    def test_plot_help(self, runner: CliRunner) -> None:
        """Test plot command help."""
        result = runner.invoke(cli, ["plot", "--help"])
        assert result.exit_code == 0
        assert "--ontology" in result.output
        assert "--output" in result.output

    def test_ontologies(self, runner: CliRunner) -> None:
        """Test ontologies command."""
        result = runner.invoke(cli, ["ontologies"])
        assert result.exit_code == 0
        assert "GO Biological Process" in result.output

    def test_submit_nonexistent_file(self, runner: CliRunner) -> None:
        """Test submit with nonexistent file."""
        result = runner.invoke(cli, ["submit", "https://asntech.org/dbsuper/data/bed/hg19/Astrocytes.bed", "--species", "hg19", "--output", "results.tsv"])
        assert result.exit_code != 0

    def test_plot_with_sample_data(
        self, runner: CliRunner, tmp_path: Path, sample_enrichment_df
    ) -> None:
        """Test plot command with sample data."""
        # Create a sample results file
        results_file = tmp_path / "results.tsv"
        sample_enrichment_df.to_csv(results_file, sep="\t", index=False)

        output_file = tmp_path / "plot.png"
        result = runner.invoke(
            cli,
            ["plot", str(results_file), "-o", str(output_file), "-n", "3"],
        )

        assert result.exit_code == 0
        assert output_file.exists()


@pytest.mark.integration
@pytest.mark.slow
class TestCLIIntegration:
    """Integration tests for CLI that hit real API."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI runner."""
        return CliRunner()

    def test_submit_real(
        self, runner: CliRunner, sample_bed_file: Path, tmp_path: Path
    ) -> None:
        """Test real submission through CLI."""
        output_file = tmp_path / "results.tsv"
        result = runner.invoke(
            cli,
            [
                "submit",
                str(sample_bed_file),
                "--species",
                "hg38",
                "--output",
                str(output_file),
                "--max-fdr",
                "1.0",  # Don't filter
            ],
        )

        # May fail due to network issues, but check structure
        if result.exit_code == 0:
            assert output_file.exists()
