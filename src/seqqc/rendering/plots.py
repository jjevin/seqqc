import plotly.graph_objects as go
import numpy as np
from scipy.ndimage import gaussian_filter1d  # For converting hist to distr

from seqqc.models.results import PerBaseQualityResult
from seqqc.models.results import PerBaseCompositionResult
from seqqc.models.results import PerReadQualityResult
from seqqc.models.results import PerReadLengthResult
from seqqc.models.results import PerReadGCResult
# TODO: Replace with import seqqc.models.results to just import all? 

def per_base_quality(result: PerBaseQualityResult) -> go.Figure:
    positions = list(range(1, len(result.medians)+1))

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

def per_base_sequence_composition(result: PerBaseCompositionResult) -> go.Figure:
    positions = list(range(1, len(result.a_percentage) + 1))

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

    # TODO: Add banding for quality? Comparing A and T or G and C?
    # Would need to be delta between those two pairs

    fig.update_layout(
        title="Per-Base Sequence Content",
        xaxis_title="Position in read (bp)",
        yaxis_title="Percent content",
        yaxis=dict(range=[0, 100]),
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_base_n_composition(result: PerBaseCompositionResult) -> go.Figure:
    positions = list(range(1, len(result.n_percentage) + 1))
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

def per_read_quality(result: PerReadQualityResult) -> go.Figure:
    positions = list(range(43))

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
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_read_length(result: PerReadLengthResult) -> go.Figure:
    positions = list(result.length_distribution.keys())
    counts = list(result.length_distribution.values())
    
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x = positions,
        y = counts,
        name='Read count'
    ))

    # TODO: Bands indicating thresholds
    # - FastQC warns if there are differing lengths, fails if there's a length of 0
    # TODO: Somway to make this look better with only 1 set of lengths?

    # TODO: Only show whole units on x axis
    fig.update_layout(
        title="Per Read Length",
        xaxis_title="Read quality (np)",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig

def per_read_gc(result: PerReadGCResult) -> go.Figure:
    positions = list(range(101))
    counts = np.array(result.gc_distribution, dtype=float)
    total = counts.sum()

    # Express as percentage of reads rather than raw counts
    frequencies = (counts / total * 100) if total > 0 else counts

    # sigma controls smoothing width -> 3 gives a curve similar to FastQC's
    smoothed = gaussian_filter1d(frequencies, sigma=3)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=positions,
        y=frequencies,
        name="Observed",
        marker_color="rgba(33, 150, 243, 0.35)",
        marker_line_width=0
    ))

    fig.add_trace(go.Scatter(
        x=positions,
        y=smoothed,
        mode="lines",
        name="Smoothed",
        line=dict(color="#1565C0", width=2)
    ))

    fig.update_layout(
        title="Per-read GC content",
        xaxis_title="GC content (%)",
        yaxis_title="Percentage of reads",
        xaxis=dict(range=[0, 100]),
        template="plotly_white",
        bargap=0,
    )

    # TODO: Add normal curve for reference
    # TODO: Add some bands to indicate quality thresholds?

    return fig
