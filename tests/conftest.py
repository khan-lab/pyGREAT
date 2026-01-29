"""Shared pytest fixtures for pygreat tests."""

from pathlib import Path

import pandas as pd
import pytest

from pygreat.models.regions import GenomicRegion, GenomicRegions


@pytest.fixture
def sample_regions() -> GenomicRegions:
    """Create sample genomic regions."""
    return GenomicRegions(
        regions=[
            GenomicRegion("chr1", 1000, 2000, "peak1"),
            GenomicRegion("chr1", 5000, 6000, "peak2"),
            GenomicRegion("chr2", 10000, 11000, "peak3"),
            GenomicRegion("chr3", 50000, 51000, "peak4"),
            GenomicRegion("chr5", 100000, 101000, "peak5"),
        ]
    )


@pytest.fixture
def sample_bed_file(tmp_path: Path, sample_regions: GenomicRegions) -> Path:
    """Create a temporary BED file."""
    bed_path = tmp_path / "test.bed"
    content = "\n".join(
        [
            "chr1\t1000\t2000\tpeak1",
            "chr1\t5000\t6000\tpeak2",
            "chr2\t10000\t11000\tpeak3",
            "chr3\t50000\t51000\tpeak4",
            "chr5\t100000\t101000\tpeak5",
        ]
    )
    bed_path.write_text(content)
    return bed_path


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame with genomic regions."""
    return pd.DataFrame(
        {
            "chrom": ["chr1", "chr1", "chr2", "chr3", "chr5"],
            "start": [1000, 5000, 10000, 50000, 100000],
            "end": [2000, 6000, 11000, 51000, 101000],
            "name": ["peak1", "peak2", "peak3", "peak4", "peak5"],
        }
    )


@pytest.fixture
def mock_submit_response() -> str:
    """Mock HTML response from submit."""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>GREAT Results</title></head>
    <body>
    <script>
    var _sessionName = "test_session_123";
    var _species = "hg38";
    </script>
    <div class="ontologyCategoryHeader">Gene Ontology</div>
    <a class="ontologyName" data-ontology="GO Molecular Function">GO Molecular Function</a>
    <a class="ontologyName" data-ontology="GO Biological Process">GO Biological Process</a>
    <a class="ontologyName" data-ontology="GO Cellular Component">GO Cellular Component</a>
    </body>
    </html>
    '''


@pytest.fixture
def mock_enrichment_js() -> str:
    """Mock JavaScript enrichment data."""
    return '''
    var enrichmentData = [
        {
            "ID": "GO:0006915",
            "name": "apoptotic process",
            "Binom_Raw_PValue": 1e-10,
            "Binom_FDR_Q_Val": 1e-8,
            "Binom_Fold_Enrichment": 5.2,
            "Hyper_Raw_PValue": 1e-9,
            "Hyper_FDR_Q_Val": 1e-7,
            "Hyper_Fold_Enrichment": 4.8,
            "Hyper_Observed_Gene_Hits": 25,
            "Hyper_Total_Genes": 500,
            "Binom_Observed_Region_Hits": 30
        },
        {
            "ID": "GO:0008150",
            "name": "biological process",
            "Binom_Raw_PValue": 1e-5,
            "Binom_FDR_Q_Val": 1e-3,
            "Binom_Fold_Enrichment": 2.1,
            "Hyper_Raw_PValue": 1e-4,
            "Hyper_FDR_Q_Val": 1e-2,
            "Hyper_Fold_Enrichment": 1.9,
            "Hyper_Observed_Gene_Hits": 10,
            "Hyper_Total_Genes": 1000,
            "Binom_Observed_Region_Hits": 15
        }
    ];
    '''


@pytest.fixture
def sample_enrichment_df() -> pd.DataFrame:
    """Create a sample enrichment results DataFrame."""
    return pd.DataFrame(
        {
            "term_id": ["GO:0006915", "GO:0008150", "GO:0016020"],
            "term_name": ["apoptotic process", "biological process", "membrane"],
            "binom_p": [1e-10, 1e-5, 1e-3],
            "binom_fdr": [1e-8, 1e-3, 0.01],
            "binom_fold_enrichment": [5.2, 2.1, 1.5],
            "hyper_p": [1e-9, 1e-4, 1e-2],
            "hyper_fdr": [1e-7, 1e-2, 0.1],
            "hyper_fold_enrichment": [4.8, 1.9, 1.3],
            "observed_genes": [25, 10, 5],
            "total_genes": [500, 1000, 200],
            "observed_regions": [30, 15, 8],
        }
    )


@pytest.fixture
def mock_batch_response() -> str:
    """Mock batch TSV response from GREAT."""
    return """<script>console.log( 'outputDir: /scratch/great/tmp/results/test.d/') ; </script># GREAT version 4.0.4\tSpecies assembly: hg38\tAssociation rule: Basal+extension: 5000 bp upstream, 1000 bp downstream, 1000000 bp max extension, curated regulatory domains included
# Ontology summary statistics are provided in the footer.
#
# Ontology\tID\tDesc\tBinomRank\tBinomP\tBinomBonfP\tBinomFdrQ\tRegionFoldEnrich\tExpRegions\tObsRegions\tGenomeFrac\tSetCov\tHyperRank\tHyperP\tHyperBonfP\tHyperFdrQ\tGeneFoldEnrich\tExpGenes\tObsGenes\tTotalGenes\tGeneSetCov\tTermCov\tRegions\tGenes
GO Biological Process\tGO:0006915\tapoptotic process\t1\t1.0e-10\t1.0e-8\t1.0e-8\t5.2\t5.8\t30\t1.0e-3\t0.03\t1\t1.0e-9\t1.0e-7\t1.0e-7\t4.8\t5.2\t25\t500\t0.05\t0.5\tpeak1,peak2\tGENE1,GENE2
GO Biological Process\tGO:0008150\tbiological process\t2\t1.0e-5\t1.0e-3\t1.0e-3\t2.1\t7.1\t15\t2.0e-3\t0.015\t2\t1.0e-4\t1.0e-2\t1.0e-2\t1.9\t5.3\t10\t1000\t0.01\t0.1\tpeak3\tGENE3
GO Molecular Function\tGO:0003674\tmolecular_function\t1\t1.0e-8\t1.0e-6\t1.0e-6\t4.5\t4.4\t20\t1.5e-3\t0.02\t1\t1.0e-7\t1.0e-5\t1.0e-5\t4.2\t4.8\t20\t400\t0.05\t0.5\tpeak1,peak4\tGENE4,GENE5
#
# Ontology\tTermsTested\tMinAnnotCount\tMaxAnnotCount
#
# GO Biological Process\t13145\t1\tInf
# GO Molecular Function\t4219\t1\tInf"""


@pytest.fixture
def mock_batch_response_empty() -> str:
    """Mock empty batch TSV response."""
    return """<script>console.log( 'outputDir: /scratch/great/tmp/results/test.d/') ; </script># GREAT version 4.0.4\tSpecies assembly: hg38\tAssociation rule: Basal+extension
# Ontology summary statistics are provided in the footer.
#
# Ontology\tID\tDesc\tBinomRank\tBinomP\tBinomBonfP\tBinomFdrQ
#
# Ontology\tTermsTested\tMinAnnotCount\tMaxAnnotCount
#"""
