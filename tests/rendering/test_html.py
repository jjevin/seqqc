from pathlib import Path
import pytest

from seqqc.models.results import QCResult, ReadCountResult, PerBaseQualityResult
from seqqc.rendering.html import render_report

@pytest.fixture
def minimal_result() -> QCResult:
    return QCResult(
        filename="sample.fastq",
        read_count=ReadCountResult(value=1000),
        per_base_quality=PerBaseQualityResult(
            first_deciles=[1, 1, 1],
            first_quartiles=[2, 2, 2],
            medians=[3, 3, 3],
            third_quartiles=[4, 4, 4],
            ninth_deciles=[5, 5, 5],
            means=[3, 3, 3],
            decay_constant=0,
            decay_initial_quality=0,
            decay_r_squared=0
        )
    )

class TestRenderReport:
    def test_creates_output_file(self, minimal_result, tmp_path):
        out = tmp_path / "report.html"
        render_report(minimal_result, out)
        assert out.exists()

    def test_output_is_valid_html(self, minimal_result, tmp_path):
        out = tmp_path / "report.html"
        render_report(minimal_result, out)
        content = out.read_text()
        assert content.startswith("<!DOCTYPE html>")

    def test_filename_appers_in_report(self, minimal_result, tmp_path):
        out = tmp_path / "report.html"
        render_report(minimal_result, out)
        assert "sample.fastq" in out.read_text()

    def test_readcount_appears_in_report(self, minimal_result, tmp_path):
        out = tmp_path / "report.html"
        render_report(minimal_result, out)
        assert "1000" in out.read_text()

    def test_plot_div_is_embedded(self, minimal_result, tmp_path):
        out = tmp_path / "report.html"
        render_report(minimal_result, out)
        # Plotly embeds figures inside a <div> with class "plotly-graph-div"
        assert "plotly-graph-div" in out.read_text()

    def test_missing_metric_does_not_raise(self, tmp_path):
        result = QCResult(filename="empty.fastq")
        out = tmp_path / "report.html"
        render_report(result, out) # Should not raise exception
        assert out.exists()
