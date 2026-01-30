# Contributing

Thank you for your interest in contributing to pyGREAT! This guide will help you get started.

## Development Setup

### Clone the Repository

```bash
git clone https://github.com/khan-lab/pyGREAT.git
cd pyGREAT
```

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs pygreat in editable mode with all development dependencies.

## Code Style

pygreat uses modern Python 3.10+ features and follows these conventions:

### Type Hints

All public functions and methods must have complete type hints:

```python
def submit_job(
    self,
    regions: str | Path | pd.DataFrame,
    species: Species = "hg38",
    *,
    background: str | None = None,
) -> GreatJob:
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def parse(self, content: str) -> dict[str, pd.DataFrame]:
    """Parse batch TSV content.

    Args:
        content: Raw TSV content from GREAT API.

    Returns:
        Dictionary mapping ontology names to DataFrames.

    Raises:
        ParsingError: If content cannot be parsed.
    """
```

### Linting

Run ruff for linting:

```bash
ruff check src tests
ruff format src tests
```

### Type Checking

Run mypy for type checking:

```bash
mypy src
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run with Coverage

```bash
pytest --cov=pygreat --cov-report=html
open htmlcov/index.html
```

### Run Integration Tests

Integration tests hit the real GREAT server and are slow:

```bash
pytest -m integration
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use fixtures from `tests/conftest.py`
- Mock external HTTP calls in unit tests

Example test:

```python
import pytest
from pygreat.api.parser import BatchResponseParser


class TestBatchResponseParser:
    """Tests for BatchResponseParser."""

    @pytest.fixture
    def parser(self) -> BatchResponseParser:
        return BatchResponseParser()

    def test_parse_empty(self, parser: BatchResponseParser) -> None:
        """Test parsing empty content."""
        result = parser.parse("")
        assert result == {}

    def test_parse_valid(
        self, parser: BatchResponseParser, mock_batch_response: str
    ) -> None:
        """Test parsing valid TSV response."""
        results = parser.parse(mock_batch_response)
        assert "GO Biological Process" in results
```

## Documentation

### Build Documentation Locally

```bash
pip install mkdocs-material mkdocstrings[python]
mkdocs serve
```

Visit `http://127.0.0.1:8000` to preview.

### Documentation Structure

```
docs/
├── index.md              # Home page
├── getting-started/      # Installation and quickstart
├── guide/                # User guides
├── api/                  # API reference
├── examples/             # Code examples
├── contributing.md       # This file
└── changelog.md          # Version history
```

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the style guide
- Add tests for new functionality
- Update documentation as needed

### 3. Run Checks

```bash
# Lint
ruff check src tests
ruff format --check src tests

# Type check
mypy src

# Test
pytest
```

### 4. Commit

Write clear commit messages:

```
Add support for URL inputs in submit_job

- Skip file upload when input is a URL
- Add _is_url() helper function
- Update documentation
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Project Structure

```
pyGREAT/
├── src/pygreat/
│   ├── __init__.py        # Package exports
│   ├── core/
│   │   ├── client.py      # GreatClient
│   │   ├── job.py         # GreatJob
│   │   ├── config.py      # Constants
│   │   └── exceptions.py  # Custom exceptions
│   ├── api/
│   │   ├── http.py        # HTTP client
│   │   └── parser.py      # Response parsers
│   ├── models/
│   │   ├── regions.py     # GenomicRegions
│   │   └── enrichment.py  # EnrichmentResult
│   ├── viz/
│   │   ├── barplot.py     # Bar plots
│   │   └── dotplot.py     # Dot plots
│   └── cli/
│       └── app.py         # CLI application
├── tests/
│   ├── conftest.py        # Fixtures
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
├── pyproject.toml         # Package config
└── README.md
```

## Areas for Contribution

### Good First Issues

- Add more test coverage
- Improve error messages
- Add examples to documentation
- Fix typos

### Feature Ideas

- Async client support
- Additional visualization types
- Support for more file formats
- Caching mechanisms

### Documentation

- Add more examples
- Improve API documentation
- Add tutorials
- Translate documentation

## Questions?

Feel free to open an issue on GitHub for:

- Bug reports
- Feature requests
- Questions about the code
- Help with contributions

Thank you for contributing!
