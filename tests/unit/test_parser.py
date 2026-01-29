"""Tests for parsers."""

import pytest

from pygreat.api.parser import BatchResponseParser, ResponseParser
from pygreat.core.exceptions import ParsingError


class TestBatchResponseParser:
    """Tests for BatchResponseParser class."""

    @pytest.fixture
    def parser(self) -> BatchResponseParser:
        """Create parser instance."""
        return BatchResponseParser()

    def test_parse_batch_response(
        self, parser: BatchResponseParser, mock_batch_response: str
    ) -> None:
        """Test parsing batch TSV response."""
        results = parser.parse(mock_batch_response)

        # Should have 2 ontologies
        assert len(results) == 2
        assert "GO Biological Process" in results
        assert "GO Molecular Function" in results

        # Check GO Biological Process
        go_bp = results["GO Biological Process"]
        assert len(go_bp) == 2
        assert "term_id" in go_bp.columns
        assert "term_name" in go_bp.columns
        assert "binom_p" in go_bp.columns
        assert "binom_fdr" in go_bp.columns

        # Check first row values
        row1 = go_bp.iloc[0]
        assert row1["term_id"] == "GO:0006915"
        assert row1["term_name"] == "apoptotic process"
        assert row1["observed_genes"] == 25
        assert row1["total_genes"] == 500

        # Check GO Molecular Function
        go_mf = results["GO Molecular Function"]
        assert len(go_mf) == 1
        assert go_mf.iloc[0]["term_id"] == "GO:0003674"

    def test_parse_empty_response(
        self, parser: BatchResponseParser, mock_batch_response_empty: str
    ) -> None:
        """Test parsing empty batch response."""
        results = parser.parse(mock_batch_response_empty)
        assert results == {}

    def test_parse_empty_string(self, parser: BatchResponseParser) -> None:
        """Test parsing empty string."""
        results = parser.parse("")
        assert results == {}

    def test_parse_metadata(
        self, parser: BatchResponseParser, mock_batch_response: str
    ) -> None:
        """Test extracting metadata."""
        metadata = parser.parse_metadata(mock_batch_response)

        assert metadata["version"] == "4.0.4"
        assert metadata["species"] == "hg38"
        assert "Basal+extension" in metadata["rule"]

    def test_parse_metadata_empty(self, parser: BatchResponseParser) -> None:
        """Test metadata from empty content."""
        metadata = parser.parse_metadata("")
        assert metadata["version"] == ""
        assert metadata["species"] == ""
        assert metadata["rule"] == ""

    def test_parse_ontology_stats(
        self, parser: BatchResponseParser, mock_batch_response: str
    ) -> None:
        """Test extracting ontology stats."""
        stats = parser.parse_ontology_stats(mock_batch_response)

        assert "GO Biological Process" in stats
        assert stats["GO Biological Process"]["terms_tested"] == 13145

        assert "GO Molecular Function" in stats
        assert stats["GO Molecular Function"]["terms_tested"] == 4219

    def test_parse_numeric_conversion(
        self, parser: BatchResponseParser, mock_batch_response: str
    ) -> None:
        """Test numeric columns are properly converted."""
        results = parser.parse(mock_batch_response)
        go_bp = results["GO Biological Process"]

        # Check numeric types
        assert go_bp["binom_p"].dtype.kind == "f"  # float
        assert go_bp["observed_genes"].dtype.kind == "i"  # integer
        assert go_bp["binom_fdr"].dtype.kind == "f"  # float


class TestResponseParser:
    """Tests for ResponseParser class (legacy HTML parser)."""

    @pytest.fixture
    def parser(self) -> ResponseParser:
        """Create parser instance."""
        return ResponseParser()

    def test_parse_submit_response(
        self, parser: ResponseParser, mock_submit_response: str
    ) -> None:
        """Test parsing submit response."""
        result = parser.parse_submit_response(mock_submit_response)
        assert result["session_id"] == "test_session_123"
        assert result["species"] == "hg38"
        assert "Gene Ontology" in result["ontologies"]

    def test_parse_submit_response_error(self, parser: ResponseParser) -> None:
        """Test parsing response with error."""
        error_html = "<html>encountered a user error: invalid BED format</html>"
        with pytest.raises(ParsingError, match="GREAT server error"):
            parser.parse_submit_response(error_html)

    def test_parse_submit_response_no_session(self, parser: ResponseParser) -> None:
        """Test parsing response without session ID."""
        html = "<html><body>No session here</body></html>"
        with pytest.raises(ParsingError, match="Could not extract session ID"):
            parser.parse_submit_response(html)

    def test_parse_enrichment_js(
        self, parser: ResponseParser, mock_enrichment_js: str
    ) -> None:
        """Test parsing enrichment JavaScript."""
        df = parser.parse_enrichment_js(mock_enrichment_js)
        assert len(df) == 2
        assert "term_id" in df.columns
        assert "term_name" in df.columns
        assert df.iloc[0]["term_id"] == "GO:0006915"
        assert df.iloc[0]["term_name"] == "apoptotic process"

    def test_parse_enrichment_js_empty(self, parser: ResponseParser) -> None:
        """Test parsing empty enrichment data."""
        df = parser.parse_enrichment_js("var data = [];")
        assert df.empty

    def test_parse_enrichment_js_direct_json(self, parser: ResponseParser) -> None:
        """Test parsing direct JSON array."""
        json_data = '[{"ID": "GO:0001234", "name": "test process"}]'
        df = parser.parse_enrichment_js(json_data)
        assert len(df) == 1
        assert df.iloc[0]["term_id"] == "GO:0001234"

    def test_parse_associations(self, parser: ResponseParser) -> None:
        """Test parsing TSV associations."""
        tsv = "region\tgene\tdistance\nchr1:1000-2000\tGENE1\t500\nchr2:3000-4000\tGENE2\t1000"
        df = parser.parse_associations(tsv)
        assert len(df) == 2
        assert "region" in df.columns
        assert "gene" in df.columns

    def test_parse_associations_with_comments(self, parser: ResponseParser) -> None:
        """Test parsing TSV with comments."""
        tsv = "# Comment\nregion\tgene\nchr1:1000-2000\tGENE1"
        df = parser.parse_associations(tsv)
        assert len(df) == 1

    def test_extract_error_message(self, parser: ResponseParser) -> None:
        """Test error message extraction."""
        html = '<div class="error">Invalid input format</div>'
        msg = parser._extract_error_message(html)
        assert "Invalid input format" in msg

    def test_parse_ontologies_default(self, parser: ResponseParser) -> None:
        """Test default ontology parsing."""
        html = "<html><body>No ontology data</body></html>"
        ontologies = parser._parse_ontologies(html)
        # Should return defaults
        assert "Gene Ontology" in ontologies
