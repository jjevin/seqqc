from typer.testing import CliRunner
from seqqc.cli import app

runner = CliRunner()

def test_help_exits_cleanly():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "seqqc" in result.output
