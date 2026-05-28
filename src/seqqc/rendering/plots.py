import plotly.graph_objects as go

from seqqc.models.results import PerBaseQualityResult
from seqqc.models.results import PerBaseCompositionResult
from seqqc.models.results import PerReadQualityResult

def per_base_quality(result: PerBaseQualityResult) -> go.Figure():
    # TODO: Should be same length for all, but might want to take max anyways?
    positions = list(range(1, len(result.medians)))

    fig = go.Figure()

    # Percentiles as a histogram
    fig.add_trace(go.Box(
        q1 = result.first_quartiles,
        median = result.medians,
        q3 = result.third_quartiles,
        lowerfence = result.first_deciles,
        upperfence = result.ninth_deciles,
        # mean = result.means,
        x = positions,
        name = "Quality percentiles"
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = result.means,
        mode='lines',
        name='Means'
    ))


    # TODO: Additional trace for mean lines?

    # Background bands matching FastQC's pass/warn/fail thresholds
    # Values derived from Illumina data (see FastQC docs)
    fig.add_hrect(y0=28, y1=42, fillcolor="green",  opacity=0.09, line_width=0)
    fig.add_hrect(y0=20, y1=28, fillcolor="orange", opacity=0.09, line_width=0)
    fig.add_hrect(y0=0,  y1=20, fillcolor="red",    opacity=0.09, line_width=0)

    fig.update_layout(
        title="Per-Base Sequence Quality",
        xaxis_title="Position in read (bp)",
        yaxis_title="Phred quality score",
        yaxis=dict(range=[0, 42]),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_base_sequence_composition(result: PerBaseCompositionResult) -> go.Figure():
    # TODO: Should be same length for all, but might want to take max anyways?
    positions = list(range(1, len(result.a_percentage)))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = positions,
        y = [a * 100 for a in result.a_percentage],
        mode='lines',
        name='%A'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = [t * 100 for t in result.t_percentage],
        mode='lines',
        name='%T'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = [g * 100 for g in result.g_percentage],
        mode='lines',
        name='%G'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = [c * 100 for c in result.c_percentage],
        mode='lines',
        name='%C'
    ))

    fig.update_layout(
        title="Per-Base Sequence Content",
        xaxis_title="Position in read (bp)",
        yaxis_title="Percent content",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_base_n_composition(result: PerBaseCompositionResult) -> go.Figure():
    # TODO: Should be same length for all, but might want to take max anyways?
    positions = list(range(1, len(result.n_percentage)))
    n_percentage = [n * 100 for n in result.n_percentage]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = positions,
        y = n_percentage,
        mode='lines',
        name='%N'
    ))

    # Background bands matching FastQC's pass/warn/fail thresholds
    # Values derived from Illumina data (see FastQC docs)
    fig.add_hrect(y0=0,  y1=5,   fillcolor="green",  opacity=0.09, line_width=0)
    fig.add_hrect(y0=5,  y1=20,  fillcolor="orange", opacity=0.09, line_width=0)
    fig.add_hrect(y0=20, y1=100, fillcolor="red",    opacity=0.09, line_width=0)

    max_y = max(35, max(n_percentage) + 5)
    fig.update_layout(
        title="Per-Base N Content",
        xaxis_title="Position in read (bp)",
        yaxis_title="Percent content",
        yaxis=dict(range=[0, max_y]),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_read_quality(result: PerReadQualityResult) -> go.Figure():
    # TODO: Should be same length for all, but might want to take max anyways?
    positions = list(range(42))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x = positions,
        y = result.avg_qualities,
        name='Average Read Quality'
    ))

    # Background bands matching FastQC's pass/warn/fail thresholds
    # Values derived from Illumina data (see FastQC docs)
    fig.add_vrect(x0=27, x1=42, fillcolor="green",  opacity=0.09, line_width=0)
    fig.add_vrect(x0=20, x1=27, fillcolor="orange", opacity=0.09, line_width=0)
    fig.add_vrect(x0=0,  x1=20, fillcolor="red",    opacity=0.09, line_width=0)

    fig.update_layout(
        title="Per Read Quality Scores",
        xaxis_title="Mean read quality (Phred Score)",
        # yaxis_title="",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig
