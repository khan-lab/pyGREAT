# Exceptions

::: pygreat.core.exceptions
    options:
      show_source: false

## Overview

pygreat defines custom exceptions for handling errors that may occur during GREAT analysis.

## Exception Hierarchy

```
Exception
└── GreatError (base class)
    ├── InvalidSpeciesError
    ├── InvalidInputError
    ├── RateLimitError
    ├── ParsingError
    └── ConnectionError
```

## GreatError

Base exception for all pygreat errors.

```python
from pygreat.core.exceptions import GreatError

try:
    job = client.submit_job("peaks.bed", species="hg38")
except GreatError as e:
    print(f"GREAT error: {e}")
```

## InvalidSpeciesError

Raised when an unsupported species/genome assembly is specified.

```python
from pygreat.core.exceptions import InvalidSpeciesError

try:
    job = client.submit_job("peaks.bed", species="hg100")  # Invalid
except InvalidSpeciesError as e:
    print(f"Invalid species: {e}")
    # Invalid species: Species 'hg100' not supported in GREAT v4.0.4.
    # Supported: ('hg38', 'hg19', 'mm10', 'mm9')
```

### Supported Species

GREAT v4.0.4 supports:
- `hg38` - Human GRCh38
- `hg19` - Human GRCh37
- `mm10` - Mouse GRCm38
- `mm9` - Mouse NCBI37

## InvalidInputError

Raised when input regions are invalid or cannot be parsed.

```python
from pygreat.core.exceptions import InvalidInputError

try:
    job = client.submit_job("invalid.bed", species="hg38")
except InvalidInputError as e:
    print(f"Invalid input: {e}")
```

Common causes:
- Malformed BED file
- Missing required columns in DataFrame
- Empty input
- Invalid coordinate values

## RateLimitError

Raised when GREAT's rate limit is exceeded after all retries.

```python
from pygreat.core.exceptions import RateLimitError

try:
    job = client.submit_job("peaks.bed", species="hg38")
except RateLimitError as e:
    print(f"Rate limited: {e}")
    print("Try again later or increase max_retries")
```

### Handling Rate Limits

Configure the client for more patient retrying:

```python
client = GreatClient(
    request_interval=60.0,  # Wait 60s between retries
    max_retries=10,         # Try up to 10 times
)
```

## ParsingError

Raised when the GREAT response cannot be parsed.

```python
from pygreat.core.exceptions import ParsingError

try:
    job = client.submit_job("peaks.bed", species="hg38")
except ParsingError as e:
    print(f"Failed to parse response: {e}")
```

This usually indicates:
- GREAT server returned an error
- Unexpected response format
- Network issues causing incomplete response

## ConnectionError

Raised for network or server connectivity issues.

```python
from pygreat.core.exceptions import ConnectionError

try:
    job = client.submit_job("peaks.bed", species="hg38")
except ConnectionError as e:
    print(f"Connection failed: {e}")
```

Common causes:
- Network unavailable
- GREAT server is down
- Firewall blocking connection
- DNS resolution failed

## Error Handling Best Practices

### Catch Specific Exceptions

```python
from pygreat import GreatClient
from pygreat.core.exceptions import (
    GreatError,
    InvalidSpeciesError,
    InvalidInputError,
    RateLimitError,
    ParsingError,
    ConnectionError,
)

def run_great_analysis(bed_file, species):
    client = GreatClient()

    try:
        job = client.submit_job(bed_file, species=species)
        return job.get_enrichment_tables()

    except InvalidSpeciesError:
        print(f"Species '{species}' is not supported.")
        print("Use: hg38, hg19, mm10, or mm9")
        return None

    except InvalidInputError as e:
        print(f"Problem with input file: {e}")
        return None

    except RateLimitError:
        print("GREAT is busy. Please try again later.")
        return None

    except ParsingError as e:
        print(f"Could not parse GREAT response: {e}")
        return None

    except ConnectionError:
        print("Could not connect to GREAT server.")
        return None

    except GreatError as e:
        # Catch any other GREAT-related errors
        print(f"Unexpected error: {e}")
        return None

    finally:
        client.close()
```

### Retry Logic

```python
import time
from pygreat.core.exceptions import RateLimitError, ConnectionError

def submit_with_retry(client, bed_file, species, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return client.submit_job(bed_file, species=species)
        except (RateLimitError, ConnectionError) as e:
            if attempt < max_attempts - 1:
                wait = 60 * (attempt + 1)
                print(f"Attempt {attempt + 1} failed, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
```

### Logging Errors

```python
import logging
from pygreat.core.exceptions import GreatError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    job = client.submit_job("peaks.bed", species="hg38")
except GreatError as e:
    logger.error(f"GREAT analysis failed: {e}", exc_info=True)
    raise
```
