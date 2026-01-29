"""Integration tests for GREAT API.

These tests require network access and hit the real GREAT server.
Run with: pytest -m integration
"""

from pathlib import Path

import pytest

from pygreat import GreatClient


@pytest.mark.integration
@pytest.mark.slow
class TestGreatAPI:
    """Integration tests against real GREAT server.

    These tests are slow and hit the real API.
    They are marked with @pytest.mark.integration and @pytest.mark.slow.
    """

    def test_submit_and_retrieve(self, sample_bed_file: Path) -> None:
        """Test full workflow: submit job and retrieve results."""
        client = GreatClient()

        try:
            job = client.submit_job(sample_bed_file, species="hg38")

            # Job should have results immediately (batch API)
            assert job.job_id is not None
            assert len(job.job_id) > 0

            # Get available ontologies
            ontologies = job.list_ontologies()
            assert len(ontologies) > 0

            # Get enrichment results
            results = job.get_enrichment_tables(max_fdr=1.0)

            # Should have some ontologies with results
            assert len(results) > 0

            # Check metadata
            metadata = job.get_metadata()
            assert metadata["species"] == "hg38"
        finally:
            client.close()

    def test_submit_with_background(
        self, sample_bed_file: Path, tmp_path: Path
    ) -> None:
        """Test submission with background regions."""
        # Create a background file with more regions
        bg_file = tmp_path / "background.bed"
        bg_content = "\n".join(
            [f"chr{i}\t{j*1000}\t{j*1000+1000}\tpeak{i}_{j}"
             for i in range(1, 6) for j in range(1, 20)]
        )
        bg_file.write_text(bg_content)

        client = GreatClient()
        try:
            job = client.submit_job(
                sample_bed_file,
                species="hg38",
                background=bg_file,
            )
            assert job.job_id is not None
            assert job.species == "hg38"
        finally:
            client.close()

    def test_different_species(self, sample_bed_file: Path) -> None:
        """Test submission with different species."""
        client = GreatClient()
        try:
            # Test mouse assembly
            job = client.submit_job(sample_bed_file, species="mm10")
            assert job.job_id is not None
            assert job.species == "mm10"
        finally:
            client.close()

    def test_different_rules(self, sample_bed_file: Path) -> None:
        """Test submission with different association rules."""
        client = GreatClient()
        try:
            for rule in ["basalPlusExt", "twoClosest", "oneClosest"]:
                job = client.submit_job(
                    sample_bed_file,
                    species="hg38",
                    rule=rule,  # type: ignore
                )
                assert job.job_id is not None
                assert job.rule == rule
        finally:
            client.close()

    def test_export_to_dataframe(self, sample_bed_file: Path) -> None:
        """Test exporting results to DataFrame."""
        client = GreatClient()
        try:
            job = client.submit_job(sample_bed_file, species="hg38")

            # Export all results
            df = job.to_dataframe()

            # Should have ontology column when exporting all
            if not df.empty:
                assert "ontology" in df.columns
                assert "term_id" in df.columns
                assert "term_name" in df.columns
        finally:
            client.close()
