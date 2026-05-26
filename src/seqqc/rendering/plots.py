import plotly.graph_objects as go

from seqqc.models.results import PerBaseQualityResult
from seqqc.models.results import PerBaseCompositionResult

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
        mean = result.means,
        name = "Quality percentiles"
    ))

    # TODO: Additional trace for mean lines?

    # Background bands matching FastQC's pass/warn/fail thresholds
    # Values derived from Illumina data (see FastQC docs)
    fig.add_hrect(y0=28, y1=42, fillcolor="green",  opacity=0.09, line_width=0)
    fig.add_hrect(y0=20, y1=28, fillcolor="orange", opacity=0.09, line_width=0)
    fig.add_hrect(y0=0,  y1=20, fillcolor="red",    opacity=0.09, line_width=0)

    fig.update_layout(
        title="Per-base sequence quality",
        xaxis_title="Position in read (bp)",
        yaxis_title="Phred quality score",
        yaxis=dict(range=[0, 42]),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_base_composition(result: PerBaseCompositionResult) -> go.Figure():
    # TODO: Should be same length for all, but might want to take max anyways?
    positions = list(range(1, len(result.a_percentage)))

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = positions,
        y = result.a_percentage,
        mode='lines',
        name='%A'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = result.t_percentage,
        mode='lines',
        name='%T'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = result.g_percentage,
        mode='lines',
        name='%G'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = result.c_percentage,
        mode='lines',
        name='%C'
    ))

    fig.add_trace(go.Scatter(
        x = positions,
        y = result.n_percentage,
        mode='lines',
        name='%N'
    ))

    fig.update_layout(
        title="Per-base sequence content",
        xaxis_title="Position in read (bp)",
        yaxis_title="Percent content",
        # yaxis=dict(range=[0, 100]),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig
