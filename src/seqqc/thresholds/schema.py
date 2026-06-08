from __future__ import annotations
from pathlib import Path
from typing import Self		# Python < 3.10 would return "ThresholdConfi"
import yaml
from pydantic import BaseModel

class ThresholdPair(BaseModel):
    """Pair of warning and failure thresholds for a single metric.
    No automatic validation is applied, but for results to be reasonable
    ensure that:
    - For minimum checks (e.g., quality), warn > fail
    - For maximum checks (e.g., n_fraction), warn < fail
    """
    warn: float
    fail: float

class ThresholdConfig(BaseModel):
    min_mean_quality:     ThresholdPair | None = None # per-read mean quality
    max_adapter_fraction: ThresholdPair | None = None
    max_duplication_rate: ThresholdPair | None = None
    max_n_fraction:       ThresholdPair | None = None
    max_decay_constant:   ThresholdPair | None = None
    min_decay_r_squared:  ThresholdPair | None = None
    max_gc_content_diff:  ThresholdPair | None = None
    
    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        return cls(**yaml.safe_load(path.read_text()))
