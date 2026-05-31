from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from seqqc.models.results import QCResult
from seqqc.rendering import plots

def render_report(result: QCResult, output: Path) -> None:
    """Render a QCResult to a self-contained HTML report at 'output'"""
    figures = []

    # TODO: Is there a better way to do this? This is becoming pretty repetitive
    if result.per_base_quality is not None:
        figures.append(plots.per_base_quality(result.per_base_quality))

    if result.per_base_composition is not None:
        figures.append(plots.per_base_sequence_composition(result.per_base_composition))
        figures.append(plots.per_base_n_composition(result.per_base_composition))

    if result.per_read_quality is not None:
        figures.append(plots.per_read_quality(result.per_read_quality))

    if result.per_read_length is not None:
        figures.append(plots.per_read_length(result.per_read_length))

    if result.per_read_gc is not None:
        figures.append(plots.per_read_gc(result.per_read_gc))
    
    # Each figure becomes an HTML fragment
    # include_plotlyjs=False because the template loads it once from CDN
    plot_fragments = [
        fig.to_html(full_html=False, include_plotlyjs=False)
        for fig in figures
    ]

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=False,   # we ahndle safetly explicitly with the | safe filter
    )
    template = env.get_template("report.html.j2")
    html = template.render(result=result, plots=plot_fragments)

    output.write_text(html, encoding="utf-8")
