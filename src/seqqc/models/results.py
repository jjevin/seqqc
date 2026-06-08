from pydantic import BaseModel, ConfigDict
from collections import Counter
from enum import Enum

class MetricResult(BaseModel):
    metric_name: str

class ReadCountResult(MetricResult):
    metric_name: str = "read_count"
    value: int

class PerBaseQualityResult(MetricResult):
    metric_name: str = "per_base_quality"
    first_deciles:         list[float]
    first_quartiles:       list[float]
    medians:               list[float]
    third_quartiles:       list[float]
    ninth_deciles:         list[float]
    means:                 list[float]
    decay_initial_quality: float
    decay_constant:        float
    decay_r_squared:       float

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
    length_distribution: dict[int, int] # length -> read count
    mean: float
    median: float
    n50: int
    
class PerReadGCResult(MetricResult):
    metric_name: str = "per_read_gc"
    gc_distribution: list[float]
    mean_gc: float

class CheckStatus(Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"

class EvaluationResult(BaseModel):
    checks: dict[str, CheckStatus]
    # TODO: Look up ConfigDict use cases
    model_config = ConfigDict(use_enum_values=False)

    @property
    def passed_all(self) -> bool:
        """True only when every configured check passes (warnings not blocking)"""
        return all(s in (CheckStatus.PASS, CheckStatus.WARN)
                   for s in self.checks.values())

    @property
    def failed_checks(self) -> list[str]:
        return [name for name, status in self.checks.items()
                if status == CheckStatus.FAIL]
    @property
    def warned_checks(self) -> list[str]:
        return [name for name, status in self.checks.items()
                if status == CheckStatus.WARN]


class QCResult(BaseModel):
    filename: str
    read_count:           ReadCountResult          | None = None
    per_base_quality:     PerBaseQualityResult     | None = None
    per_base_composition: PerBaseCompositionResult | None = None
    per_read_quality:     PerReadQualityResult     | None = None
    per_read_length:      PerReadLengthResult      | None = None
    per_read_gc:          PerReadGCResult          | None = None
    # TODO: future metric results added here as optional fields
    evaluation:           EvaluationResult         | None = None
