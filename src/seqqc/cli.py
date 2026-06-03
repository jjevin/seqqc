from pathlib import Path
import typer
from seqqc.runner import analyze

app = typer.Typer(
    name="seqqc",
    help="FASTQ quality analysis tool supporting multi-file comparison.",
)

@app.command()
def run(
    file: Path = typer.Argument(
        ...,
        help = "Path to a FASTQ file.",
        exists = True,
        readable = True,
    ),
    output: Path = typer.Option(
        Path("report.html"),
        "--output", "-o",
        help = "Path for the output HTML report.",
    ),
    json_output: Path | None = typer.Option(
        None,
        "--json", "-j",
        help = "Write results as JSON to this path."
    )
) -> None:
    """Run quality analysis on a single fastq file"""
    result = analyze(file, output, json_path=json_output)
    typer.echo(f"Report written to {output}	({result.read_count.value:,} reads)")

@app.command()
def compare(
    files: list[Path] = typer.Argument(
    ...,
    help = "Two or more FASTQ files to compare",
    ),
    output: Path = typer.Option(
        Path("batch_report.html"),
        "--output", "-o",
        help = "Path for the output html report.",
    ),
) -> None:
    """Run quality analysis across multiple FASTQ files and compare results"""
    if len(files) < 2:
        typer.echo("Error: compare requires at least two files.", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Comparing {len(files)} files -> {output}")

if __name__ == "__main__":
    app()
