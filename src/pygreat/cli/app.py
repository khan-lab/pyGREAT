"""Command-line interface for pygreat."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import rich_click as click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from pygreat import __version__
from pygreat.core.client import GreatClient
from pygreat.core.exceptions import GreatError

if TYPE_CHECKING:
    import pandas as pd

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
click.rich_click.STYLE_ERRORS_SUGGESTION = "magenta italic"
click.rich_click.ERRORS_SUGGESTION = "Try running '--help' for more information."

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="pygreat")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    **pygreat** - Programmatic access to GREAT (Genomic Regions Enrichment of Annotations Tool).

    Submit genomic regions to the Stanford GREAT server and retrieve
    functional enrichment results.

    ## Examples

    Submit a BED file and get results:

        $ pygreat submit peaks.bed --species hg38 --output results.tsv

    Visualize enrichment results:

        $ pygreat plot results.tsv --ontology "GO Biological Process" -o enrichment.png
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
#@click.argument("bed_file", type=click.Path(exists=True, path_type=Path))
@click.argument("bed_file", type=str)
@click.option(
    "--species",
    "-s",
    type=click.Choice(["hg38", "hg19", "mm10", "mm9"]),
    default="hg38",
    show_default=True,
    help="Genome assembly",
)
@click.option(
    "--background",
    "-b",
    type=click.Path(exists=True, path_type=Path),
    help="Background regions BED file",
)
@click.option(
    "--rule",
    "-r",
    type=click.Choice(["basalPlusExt", "twoClosest", "oneClosest"]),
    default="basalPlusExt",
    show_default=True,
    help="Gene association rule",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file path (TSV format)",
)
@click.option(
    "--ontology",
    "-t",
    multiple=True,
    help="Specific ontologies to retrieve (can be repeated)",
)
@click.option(
    "--max-fdr",
    type=float,
    default=0.05,
    show_default=True,
    help="Maximum FDR threshold for filtering",
)
@click.option(
    "--min-genes",
    type=int,
    default=2,
    show_default=True,
    help="Minimum genes per term",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["tsv", "csv", "json"]),
    default="tsv",
    show_default=True,
    help="Output format",
)
@click.pass_context
def submit(
    ctx: click.Context,
    bed_file: Path,
    species: str,
    background: Path | None,
    rule: str,
    output: Path | None,
    ontology: tuple[str, ...],
    max_fdr: float,
    min_genes: int,
    output_format: str,
) -> None:
    """
    Submit genomic regions to GREAT for enrichment analysis.

    **BED_FILE** is the path to your genomic regions in BED format.

    ## Examples

    Basic submission:

        $ pygreat submit peaks.bed --species hg38

    With background and output:

        $ pygreat submit peaks.bed -s hg38 -b background.bed -o results.tsv

    Filter by FDR:

        $ pygreat submit peaks.bed --max-fdr 0.01 --min-genes 5 -o results.tsv
    """
    verbose = ctx.obj["verbose"]

    try:
        client = GreatClient()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            # Submit job
            task = progress.add_task("Submitting job to GREAT server...", total=None)
            job = client.submit_job(
                bed_file,
                species=species,  # type: ignore
                background=background,
                rule=rule,  # type: ignore
            )
            progress.update(task, completed=True)

            if verbose:
                console.print(f"[green]Job submitted:[/green] {job.job_id}")

            # Get results
            task = progress.add_task("Retrieving enrichment results...", total=None)
            results = job.get_enrichment_tables(
                ontologies=list(ontology) if ontology else None,
                max_fdr=max_fdr,
                min_genes=min_genes,
            )
            progress.update(task, completed=True)

        # Display summary
        _display_results_summary(results)

        # Save output
        if output:
            _save_results(results, output, output_format)
            console.print(f"\n[green]Results saved to:[/green] {output}")

        client.close()

    except GreatError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(130)


@cli.command()
@click.argument("results_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--ontology",
    "-t",
    help="Ontology to plot (uses first available if not specified)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    required=True,
    help="Output image path (png, pdf, svg)",
)
@click.option(
    "--n-terms",
    "-n",
    type=int,
    default=15,
    show_default=True,
    help="Number of terms to display",
)
@click.option(
    "--plot-type",
    type=click.Choice(["bar", "dot"]),
    default="bar",
    show_default=True,
    help="Type of plot",
)
@click.option(
    "--title",
    help="Plot title (auto-generated if not specified)",
)
@click.option(
    "--dpi",
    type=int,
    default=300,
    show_default=True,
    help="Output resolution for raster formats",
)
def plot(
    results_file: Path,
    ontology: str | None,
    output: Path,
    n_terms: int,
    plot_type: str,
    title: str | None,
    dpi: int,
) -> None:
    """
    Create visualizations from enrichment results.

    **RESULTS_FILE** is the TSV/CSV file from a previous `submit` command.

    ## Examples

    Create a bar plot:

        $ pygreat plot results.tsv -t "GO Biological Process" -o enrichment.png

    Create a dot plot:

        $ pygreat plot results.tsv --plot-type dot -o dotplot.pdf --n-terms 25
    """
    import pandas as pd

    from pygreat.viz.barplot import plot_enrichment_bar
    from pygreat.viz.dotplot import plot_enrichment_dot

    # Load results
    sep = "," if results_file.suffix == ".csv" else "\t"
    try:
        data = pd.read_csv(results_file, sep=sep)
    except Exception as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        sys.exit(1)

    # Filter by ontology if specified
    if ontology and "ontology" in data.columns:
        data = data[data["ontology"] == ontology]
    elif "ontology" in data.columns and not ontology:
        # Use first available ontology
        available = data["ontology"].unique()
        if len(available) > 0:
            ontology = available[0]
            data = data[data["ontology"] == ontology]
            console.print(f"[dim]Using ontology: {ontology}[/dim]")

    if data.empty:
        console.print("[yellow]Warning:[/yellow] No data to plot")
        return

    # Create plot
    plot_title = title or f"Top {n_terms} Enriched Terms"
    if ontology:
        plot_title = f"{ontology}: {plot_title}"

    try:
        if plot_type == "bar":
            fig, ax = plot_enrichment_bar(data, n_terms=n_terms, title=plot_title)
        else:
            fig, ax = plot_enrichment_dot(data, n_terms=n_terms, title=plot_title)

        fig.savefig(output, dpi=dpi, bbox_inches="tight")
        console.print(f"[green]Plot saved to:[/green] {output}")
    except Exception as e:
        console.print(f"[red]Error creating plot:[/red] {e}")
        sys.exit(1)


@cli.command()
def ontologies() -> None:
    """List available ontology categories in GREAT.

    Shows the default ontologies that can be retrieved with the submit command.
    """
    table = Table(title="Available Ontologies")
    table.add_column("Category", style="cyan")
    table.add_column("Ontologies", style="white")

    # Default GREAT ontologies
    ontology_info = {
        "Gene Ontology": [
            "GO Molecular Function",
            "GO Biological Process",
            "GO Cellular Component",
        ],
        "Pathway Data": ["MSigDB Pathway", "PANTHER Pathway"],
        "Disease": ["Disease Ontology", "Mouse Phenotype"],
        "Regulatory": ["ENCODE Histone", "ENCODE DNase"],
    }

    for category, names in ontology_info.items():
        table.add_row(category, "\n".join(names))

    console.print(table)
    console.print(
        "\n[dim]Note: Available ontologies may vary depending on the GREAT version.[/dim]"
    )


def _display_results_summary(results: dict[str, "pd.DataFrame"]) -> None:
    """Display a rich table summary of results."""
    import pandas as pd

    table = Table(title="Enrichment Results Summary")
    table.add_column("Ontology", style="cyan")
    table.add_column("Total Terms", justify="right")
    table.add_column("Significant (FDR<0.05)", justify="right", style="green")
    table.add_column("Top Term", style="yellow", max_width=50)

    for ontology, df in results.items():
        if df.empty:
            table.add_row(ontology, "0", "0", "-")
            continue

        n_total = len(df)
        n_sig = 0
        top_term = "-"

        if "binom_fdr" in df.columns:
            n_sig = len(df[df["binom_fdr"] < 0.05])
            if n_sig > 0 and "term_name" in df.columns:
                top_term = str(df.nsmallest(1, "binom_fdr")["term_name"].iloc[0])

        if len(top_term) > 47:
            top_term = top_term[:47] + "..."

        table.add_row(ontology, str(n_total), str(n_sig), top_term)

    console.print(table)


def _save_results(
    results: dict[str, "pd.DataFrame"],
    output: Path,
    format: str,
) -> None:
    """Save results to file."""
    import pandas as pd

    # Combine all results
    dfs = []
    for ontology, df in results.items():
        if df.empty:
            continue
        df_copy = df.copy()
        df_copy["ontology"] = ontology
        dfs.append(df_copy)

    if not dfs:
        console.print("[yellow]Warning:[/yellow] No results to save")
        return

    combined = pd.concat(dfs, ignore_index=True)

    # Reorder columns to put ontology first
    cols = ["ontology"] + [c for c in combined.columns if c != "ontology"]
    combined = combined[cols]

    if format == "tsv":
        combined.to_csv(output, sep="\t", index=False)
    elif format == "csv":
        combined.to_csv(output, index=False)
    elif format == "json":
        combined.to_json(output, orient="records", indent=2)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
