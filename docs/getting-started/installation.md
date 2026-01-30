# Installation

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Install from PyPI

The simplest way to install pygreat is via pip:

```bash
pip install py-great
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/khan-lab/pyGREAT.git
cd pygreat
pip install -e .
```

## Dependencies

pygreat automatically installs the following dependencies:

| Package      | Purpose                        |
| ------------ | ------------------------------ |
| `httpx`      | HTTP client for API requests   |
| `pandas`     | DataFrame handling for results |
| `numpy`      | Numerical operations           |
| `rich-click` | Beautiful CLI interface        |
| `rich`       | Terminal formatting            |
| `matplotlib` | Plotting backend               |
| `seaborn`    | Statistical visualizations     |

## Optional Dependencies

For development and testing:

```bash
pip install py-great[dev]
```

This includes:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `mypy` - Static type checking
- `ruff` - Linting

## Verify Installation

After installation, verify pygreat is working:

```python
>>> from pygreat import GreatClient
>>> client = GreatClient()
>>> print(f"pygreat ready, using GREAT v{client.version}")
pygreat ready, using GREAT v4.0.4
```

Or via the command line:

```bash
pygreat --version
```

## Network Requirements

pygreat requires network access to:

1. **GREAT server** (`great.stanford.edu`) - For submitting jobs and retrieving results
2. **File hosting** (`transfer.sh`) - For uploading local BED files (only when not using URLs)

Ensure these domains are accessible from your network.
