from __future__ import annotations
from pathlib import Path
from typing import Callable
import plotly.graph_objects as go
from jinja2 import Environment, FileSystemLoader

from seqqc.models.results import MetricResult, QCResult
from seqqc.rendering import plots
from seqqc.thresholds.schema import ThresholdConfig

# Mapcs QC result field name to the plot functions for that result
# Add new metrics and plot functions here
_PLOT_REGISTRY: dict[str, list[Callable[[MetricResult, ThresholdConfig | None], go.Figure]]] = {
    "per_base_quality":     [plots.per_base_quality],
    "per_base_composition": [plots.per_base_sequence_composition,
                             plots.per_base_n_composition],
    "per_read_quality":     [plots.per_read_quality],
    "per_read_length":      [plots.per_read_length],
    "per_read_gc":          [plots.per_read_gc]
}

def _collect_figures(
    result: QCResult,
    threshold_config: ThresholdConfig | None = None,
) -> list[go.Figure]:
    figures = []
    for field_name, plot_fns in _PLOT_REGISTRY.items():
        metric_result = getattr(result, field_name)
        if metric_result is not None:
            for fn in plot_fns:
                figures.append(fn(metric_result, threshold_config))
    return figures

def render_report(
    result: QCResult,
    output: Path,
    threshold_config: ThresholdConfig | None = None,
) -> None:
    """Render a QCResult to a self-contained HTML report at 'output'"""
    # Each figure becomes an HTML fragment
    # include_plotlyjs=False because the template loads it once from CDN
    plot_fragments = [
        fig.to_html(full_html=False, include_plotlyjs=False)
        for fig in _collect_figures(result, threshold_config)
    ]

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=False,   # we handle safetly explicitly with the | safe filter
    )
    template = env.get_template("report.html.j2")
    html = template.render(result=result, plots=plot_fragments)

    output.write_text(html, encoding="utf-8")
