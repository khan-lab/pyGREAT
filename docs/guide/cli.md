# CLI Reference

pygreat provides a command-line interface for quick enrichment analysis without writing Python code.

## Installation

The CLI is installed automatically with pygreat:

```bash
pip install pygreat
```

## Global Options

```bash
pygreat [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |
| `--version` | Show version and exit |
| `--help` | Show help message |

## Commands

### submit

Submit genomic regions to GREAT for enrichment analysis.

```bash
pygreat submit [OPTIONS] REGIONS
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `REGIONS` | Path to BED file or URL to public BED file |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-s, --species` | `hg38` | Genome assembly (hg38, hg19, mm10, mm9) |
| `-o, --output` | stdout | Output TSV file path |
| `-b, --background` | None | Background regions file or URL |
| `-r, --rule` | `basalPlusExt` | Association rule |
| `--max-fdr` | 1.0 | Maximum FDR threshold |
| `--min-genes` | 1 | Minimum observed genes |
| `-t, --ontologies` | all | Ontologies to include (can repeat) |

**Examples:**

```bash
# Basic usage
pygreat submit peaks.bed --species hg38 --output results.tsv

# Short form
pygreat submit peaks.bed -s hg38 -o results.tsv

# From URL
pygreat submit https://example.com/peaks.bed -s hg38 -o results.tsv

# With background
pygreat submit peaks.bed -s hg38 -b background.bed -o results.tsv

# Filter results
pygreat submit peaks.bed -s hg38 --max-fdr 0.05 --min-genes 5 -o results.tsv

# Specific ontologies
pygreat submit peaks.bed -s hg38 -t "GO Biological Process" -t "KEGG Pathway" -o results.tsv

# Verbose mode
pygreat -v submit peaks.bed -s hg38 -o results.tsv

# Different association rule
pygreat submit peaks.bed -s hg38 --rule twoClosest -o results.tsv
```

### plot

Create visualization from enrichment results.

```bash
pygreat plot [OPTIONS] RESULTS
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `RESULTS` | Path to TSV file from `submit` command |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-t, --ontology` | Required | Ontology to plot |
| `-o, --output` | Required | Output image file path |
| `--plot-type` | `bar` | Plot type: `bar` or `dot` |
| `-n, --n-terms` | 15 | Number of top terms to show |
| `--title` | ontology name | Plot title |
| `--width` | 10 | Figure width in inches |
| `--height` | 8 | Figure height in inches |
| `--dpi` | 300 | Image resolution |

**Examples:**

```bash
# Bar plot
pygreat plot results.tsv -t "GO Biological Process" -o barplot.png

# Dot plot
pygreat plot results.tsv -t "GO Biological Process" --plot-type dot -o dotplot.png

# Custom number of terms
pygreat plot results.tsv -t "GO Biological Process" -n 20 -o barplot.png

# Custom title
pygreat plot results.tsv -t "GO Biological Process" --title "ChIP-seq Enrichment" -o plot.png

# High resolution
pygreat plot results.tsv -t "GO Biological Process" --dpi 600 -o print_quality.png

# PDF output
pygreat plot results.tsv -t "GO Biological Process" -o plot.pdf

# Custom size
pygreat plot results.tsv -t "GO Biological Process" --width 12 --height 10 -o wide_plot.png
```

## Output Format

The `submit` command outputs a TSV file with these columns:

```
ontology  term_id  term_name  binom_rank  binom_p  binom_fdr  ...
```

When writing to stdout (no `-o` option), results are formatted as a table.

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PYGREAT_TIMEOUT` | Request timeout in seconds (default: 300) |
| `PYGREAT_MAX_RETRIES` | Maximum retry attempts (default: 5) |

## Examples

### Complete Workflow

```bash
# 1. Submit job and save results
pygreat -v submit peaks.bed -s hg38 --max-fdr 0.05 -o results.tsv

# 2. Create bar plot
pygreat plot results.tsv -t "GO Biological Process" -o go_bp_bar.png

# 3. Create dot plot
pygreat plot results.tsv -t "GO Biological Process" --plot-type dot -o go_bp_dot.png
```

### Batch Processing

```bash
# Process multiple samples
for bed in samples/*.bed; do
    name=$(basename "$bed" .bed)
    pygreat submit "$bed" -s hg38 --max-fdr 0.05 -o "results/${name}.tsv"
    pygreat plot "results/${name}.tsv" -t "GO Biological Process" -o "plots/${name}.png"
done
```

### Piping Results

```bash
# View results without saving
pygreat submit peaks.bed -s hg38 | head -50

# Filter with standard tools
pygreat submit peaks.bed -s hg38 | grep "GO Biological Process" | head -20
```
