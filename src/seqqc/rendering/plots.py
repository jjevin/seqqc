import plotly.graph_objects as go
import numpy as np
from scipy.ndimage import gaussian_filter1d  # For converting hist to distr
from scipy.stats import norm  # Normal distribution comparison for gc content

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
    a = np.array(result.a_percentage) * 100
    t = np.array(result.t_percentage) * 100
    c = np.array(result.g_percentage) * 100
    g = np.array(result.c_percentage) * 100

    at_diff = np.abs(a - t)
    gc_diff = np.abs(g - c)
    max_diff = np.maximum(at_diff, gc_diff)

    fig = go.Figure()

    for i, (pos, diff) in enumerate(zip(positions, max_diff)):
        if diff > 20:
            color, opacity = "red", 0.12
        elif diff > 10:
            color, opacity = "orange", 0.10
        else:
            continue
        fig.add_vrect(x0=pos - 0.5, x1=pos + 0.5,
                      fillcolor=color, opacity=opacity, line_width=0)

    for values, name in [(a, "%A"), (t, "%T"), (g, "%G"), (c, "%C")]:
        fig.add_trace(go.Scatter(
            x=positions,
            y=values,
            mode="lines",
            name=name
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
    min_len = min(result.length_distribution)
    max_len = max(result.length_distribution)
    is_uniform = len(result.length_distribution) == 1

    # Visual padding parameters
    pad = max(5, int((max_len - min_len) * 0.1)) if not is_uniform else 10
    x_min = max(0, min_len - pad)
    x_max = max_len + pad
    
    positions = list(range(x_min, x_max + 1))
    # Convert length distribution to list, defaulting to 0 if no value found
    counts = [result.length_distribution.get(p, 0) for p in positions]
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = positions,
        y = counts,
        mode="lines",
        fill = "tozeroy",
        name="Read count",
        line = dict(color="#2196F3", width=2),
        fillcolor="rgba(33, 150, 243, 0.2)",
    ))

    # Warning annotations if lengths vary
    annotations = []
    if not is_uniform:
        annotations.append(dict(
            text="Warning: reads have variable lengths",
            xref="paper", yref="paper", x=0.01, y=0.97,
            showarrow=False, font=dict(color="orange", size=12),
        ))
    # Failure annotations if any read has a length of zero
    if 0 in result.length_distribution:
        annotations.append(dict(
            text="FAIL: zero-length reads present",
            xref="paper", yref="paper", x=0.01, y=0.91,
            showarrow=False, font=dict(color="red", size=12),
        ))

    fig.update_layout(
        title="Read length distribution",
        xaxis_title="Read length (bp)",
        yaxis_title="Read count",
        xaxis=dict(tickmode="auto", nticks=10),
        template="plotly_white",
        annotations=annotations
    )

    return fig

def per_read_gc(result: PerReadGCResult) -> go.Figure:
    x = np.arange(101)
    counts = np.array(result.gc_distribution, dtype=float)
    total = counts.sum()

    # Express as percentage of reads rather than raw counts
    frequencies = (counts / total * 100) if total > 0 else counts

    # sigma controls smoothing width -> 3 gives a curve similar to FastQC's
    smoothed = gaussian_filter1d(frequencies, sigma=3)

    # Theoretical normal distr centered at mean GC with matching std dev
    std_gc = float(np.sqrt(np.average((x - result.mean_gc) ** 2, weights=counts))) \
    	if total >  0 else 1.0
    theoretical = norm.pdf(x, loc=result.mean_gc, scale=std_gc)
    theoretical = theoretical / theoretical.sum() * 100

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(x),
        y=frequencies.tolist(),
        name="Observed",
        marker_color="rgba(33, 150, 243, 0.35)",
        marker_line_width=0
    ))

    fig.add_trace(go.Scatter(
        x=list(x),
        y=smoothed.tolist(),
        mode="lines",
        name="Smoothed",
        line=dict(color="#1565C0", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=list(x),
        y=theoretical.tolist(),
        mode="lines",
        name="Theoretical",
        line=dict(color="#E53935", width=2, dash="dash"),
    ))

    fig.update_layout(
        title="Per-read GC content",
        xaxis_title="GC content (%)",
        yaxis_title="Percentage of reads",
        xaxis=dict(range=[0, 100]),
        template="plotly_white",
        bargap=0,
    )

    return fig
