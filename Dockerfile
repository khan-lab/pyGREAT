FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/khan-lab/pyGREAT"
LABEL org.opencontainers.image.title="pyGREAT"
LABEL org.opencontainers.image.description="Python client for GREAT (Stanford)"
LABEL org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies for pip installing from source (kept minimal)
RUN pip install --no-cache-dir -U pip

# Copy only metadata first for better layer caching
COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src

RUN pip install --no-cache-dir .

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-c", "from pygreat import GreatClient; print(GreatClient().health())"]

