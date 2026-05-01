from pydantic import BaseModel

class MetricResult(BaseModel):
    metric_name: str

class ReadCountResult(MetricResult):
    metric_name: str = "read_count"
    value: int

class QCResult(BaseModel):
    filename: str
    read_count: ReadCountResult | None = None
    # TODO: future metric results added here as optional fields
