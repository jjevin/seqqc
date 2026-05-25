from pydantic import BaseModel

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

class QCResult(BaseModel):
    filename: str
    read_count: ReadCountResult | None = None
    per_base_quality: PerBaseQualityResult | None = None
    # TODO: future metric results added here as optional fields
