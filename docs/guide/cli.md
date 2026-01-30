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

### report

Generate an interactive HTML report from enrichment results.

```bash
pygreat report [OPTIONS] RESULTS_FILE
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `RESULTS_FILE` | Path to TSV/CSV file from `submit` or `local` command |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `-o, --output` | Required | Output HTML file path |
| `-t, --title` | "GREAT Enrichment Report" | Report title |
| `--fdr-threshold` | 0.05 | Default FDR threshold for filtering |
| `--top-n` | 100 | Default number of top terms to display |

**Report Features:**

- **Summary Panel** - Overview with total terms, significant terms per ontology
- **Interactive Tables** - Search, sort, pagination with DataTables
- **Global Filters** - FDR threshold, p-value threshold, Top N, category filter
- **Term Detail Modal** - Click any term to see full statistics, gene list, GO links
- **Plot Builder** - Create bar or dot plots from selected terms
- **Export Options** - Download plots (SVG/PNG) and data (TSV/CSV)

**Examples:**

```bash
# Basic report
pygreat report results.tsv -o report.html

# Custom title
pygreat report results.tsv -o report.html -t "ChIP-seq Analysis"

# Stricter FDR default
pygreat report results.tsv -o report.html --fdr-threshold 0.01

# Show fewer terms by default
pygreat report results.tsv -o report.html --top-n 20
```

### local

Run GREAT enrichment analysis locally without the web service.

```bash
pygreat local [OPTIONS] REGIONS
```

**Arguments:**

| Argument | Description |
|----------|-------------|
| `REGIONS` | Path to BED file with genomic regions |

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--gtf` | Required | Path to GTF gene annotation file |
| `--gmt` | Required | Path to GMT gene set file(s), can repeat |
| `--chrom-sizes` | None | Chromosome sizes file (optional) |
| `-o, --output` | stdout | Output TSV file path |
| `--upstream` | 5000 | Basal upstream extension (bp) |
| `--downstream` | 1000 | Basal downstream extension (bp) |
| `--max-extension` | 1000000 | Maximum extension (bp) |
| `--max-fdr` | 1.0 | Maximum FDR threshold |
| `--min-genes` | 1 | Minimum observed genes |

**Examples:**

```bash
# Basic local analysis
pygreat local peaks.bed --gtf genes.gtf --gmt go_terms.gmt -o results.tsv

# Multiple gene set files
pygreat local peaks.bed --gtf genes.gtf --gmt go_bp.gmt --gmt go_mf.gmt -o results.tsv

# Custom regulatory domain
pygreat local peaks.bed --gtf genes.gtf --gmt terms.gmt \
    --upstream 10000 --downstream 2000 --max-extension 500000 -o results.tsv

# Filter results
pygreat local peaks.bed --gtf genes.gtf --gmt terms.gmt \
    --max-fdr 0.05 --min-genes 3 -o results.tsv
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

# 4. Generate interactive HTML report
pygreat report results.tsv -o report.html
```

### Local Analysis Workflow

```bash
# 1. Run local enrichment analysis
pygreat local peaks.bed --gtf gencode.gtf --gmt go_terms.gmt -o results.tsv

# 2. Generate interactive report
pygreat report results.tsv -o report.html -t "Local GREAT Analysis"
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
