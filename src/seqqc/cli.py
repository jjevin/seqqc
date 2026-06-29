from pathlib import Path
import typer
from seqqc.runner import analyze, batch_analyze
from seqqc.thresholds.schema import ThresholdConfig

app = typer.Typer(
    name="seqqc",
    help="FASTQ quality analysis tool supporting multi-file comparison.",
)


@app.command()
def run(
    file: Path = typer.Argument(
        ...,
        help="Path to a FASTQ file.",
        exists=True,
        readable=True,
    ),
    output: Path = typer.Option(
        Path("report.html"),
        "--output",
        "-o",
        help="Path for the output HTML report.",
    ),
    json_output: Path | None = typer.Option(
        None, "--json", "-j", help="Write results as JSON to this path."
    ),
    thresholds: Path | None = typer.Option(
        None,
        "--thresholds",
        "-t",
        help="Path for metric failure threshold configuration",
    ),
) -> None:
    """Run quality analysis on a single fastq file"""
    config = ThresholdConfig.from_yaml(thresholds) if thresholds else None
    result = analyze(file, output, json_path=json_output, threshold_config=config)
    # TODO: need null checking for value here
    typer.echo(f"Report written to {output}	({result.read_count.value} reads)")

    if not result.evaluation:
        return None
    if result.evaluation.failed_checks:
        typer.echo(f"FAIL: {', '.join(result.evaluation.failed_checks)}", err=True)
        # TODO: Blocks warnings from printing
        # raise typer.Exit(code=1)
    if result.evaluation.warned_checks:
        typer.echo(f"WARN: {', '.join(result.evaluation.warned_checks)}", err=True)


@app.command()
def compare(
    files: list[Path] = typer.Argument(
        ...,
        help="Two or more FASTQ files to compare",
    ),
    output: Path = typer.Option(
        Path("batch_report.html"),
        "--output",
        "-o",
        help="Path for the output html report.",
    ),
    thresholds: Path | None = typer.Option(
        None,
        "--thresholds",
        "-t",
        help="Path for metric failure threshold configuration",
    ),
) -> None:
    """Run quality analysis across multiple FASTQ files and compare results"""
    if len(files) < 2:
        typer.echo("Error: compare requires at least two files.", err=True)
        raise typer.Exit(code=1)

    config = ThresholdConfig.from_yaml(thresholds) if thresholds else None
    typer.echo(f"Processing {len(files)} files...")
    results = batch_analyze(files, output, threshold_config=config)

    failing = [
        r.filename for r in results if r.evaluation and r.evaluation.failed_checks
    ]
    if failing:
        typer.echo(
            f"FAIL: {len(failing)} sample(s) failed thresholds: "
            f"{', '.join(failing)}, err=True"
        )
        raise typer.Exit(code=1)

    typer.echo(f"Batch report written to {output}  ({len(results)} samples)")


if __name__ == "__main__":
    app()
