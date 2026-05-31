from pydantic import BaseModel

from collections import Counter

class MetricResult(BaseModel):
    metric_name: str

class ReadCountResult(MetricResult):
    metric_name: str = "read_count"
    value: int

class PerBaseQualityResult(MetricResult):
    metric_name: str = "per_base_quality"
    first_deciles:   list[float]
    first_quartiles: list[float]
    medians:         list[float]
    third_quartiles: list[float]
    ninth_deciles:   list[float]
    means:           list[float]

class PerBaseCompositionResult(MetricResult):
    metric_name: str = "per_base_composition"
    a_percentage: list[float]
    t_percentage: list[float]
    g_percentage: list[float]
    c_percentage: list[float]
    n_percentage: list[float]

class PerReadQualityResult(MetricResult):
    metric_name: str = "per_read_quality"
    avg_qualities: list[int]

class PerReadLengthResult(MetricResult):
    metric_name: str = "per_read_length"
    length_counter: Counter
    #read_lengths: list[int]

class PerReadGCResult(MetricResult):
    metric_name: str = "per_read_gc"
    gc_distribution: list[float]
    mean_gc: float

class QCResult(BaseModel):
    filename: str
    read_count:           ReadCountResult          | None = None
    per_base_quality:     PerBaseQualityResult     | None = None
    per_base_composition: PerBaseCompositionResult | None = None
    per_read_quality:     PerReadQualityResult     | None = None
    per_read_length:      PerReadLengthResult      | None = None
    per_read_gc:          PerReadGCResult          | None = None
    # TODO: future metric results added here as optional fields
