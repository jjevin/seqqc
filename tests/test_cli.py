import pytest
from pathlib import Path
from typer.testing import CliRunner
from seqqc.cli import app

runner = CliRunner()

# Run
class TestRunCommand:
    def test_help_exits_cleanly(self):
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0

    def test_run_accepts_valid_file(self, simple_fastq_file: Path):
        result = runner.invoke(app, ["run", str(simple_fastq_file)])
        assert result.exit_code == 0

    def test_run_rejects_missing_file(self, tmp_path: Path, simple_fastq_file: Path):
        missing_file = tmp_path / "ghost.fastq"
        result = runner.invoke(app, ["run", str(missing_file)])
        assert result.exit_code != 0
        

# Compare
class TestCompareCommand:
    def test_help_exits_cleanly(self):
        result = runner.invoke(app, ["compare", "--help"])
        assert result.exit_code == 0

    def test_compare_rejects_single_file(self, simple_fastq_file: Path):
        result = runner.invoke(app, ["compare", str(simple_fastq_file)])
        assert result.exit_code == 1

    def test_compare_accepts_two_files(self, simple_fastq_file: Path, single_read_file: Path):
        result = runner.invoke(app, [
            "compare",
            str(simple_fastq_file),
            str(single_read_file),
        ])
        assert result.exit_code == 0
