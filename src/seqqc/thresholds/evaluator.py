from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Callable, Any

from seqqc.models.results import CheckStatus, EvaluationResult, QCResult
from seqqc.thresholds.schema import ThresholdConfig

# Moved to helper function to guard against ZeroDivisionError
def _weighted_mean(counts: list[int]) -> float:
    arr = np.array(counts, dtype=float)
    if arr.sum() == 0:
        return 0.0
    return float(np.average(np.arange(len(arr)), weights=arr))

def _gc_max_diff(
    a_percentage: list,
    t_percentage: list,
    c_percentage: list,
    g_percentage: list,
) -> float:
    a = np.array(a_percentage)
    t = np.array(t_percentage)
    c = np.array(c_percentage)
    g = np.array(g_percentage)

    at_diff = np.abs(a - t)
    gc_diff = np.abs(g - c)
    max_diff = np.maximum(at_diff, gc_diff)

    return np.max(max_diff)

# TODO: Check out frozen=True -> indicates immuntable registry?
@dataclass(frozen=True)
class Check:
    config_field: str                        # attribute name on ThresholdConfig
    result_field: str                        # attribute name on QCResult
    predicate: Callable[[Any, float], bool]  # (metric_result, threshold) -> pass?

_CHECKS: dict[str, Check] = {
    "min_mean_quality": Check(
        config_field="min_mean_quality",
        result_field="per_read_quality",
        predicate=lambda m, t: _weighted_mean(m.avg_qualities) >= t,
    ),
    "max_n_fraction": Check(
        config_field="max_n_fraction",
        result_field="per_base_composition",
        predicate=lambda m, t: max(m.n_percentage) <= t,
    ),
    "max_decay_constant": Check(
        config_field="max_decay_constant",
        result_field="per_base_quality",
        predicate=lambda m, t: m.decay_constant <= t,
    ),
    "min_decay_r_squared": Check(
        config_field="min_decay_r_squared",
        result_field="per_base_quality",
        predicate=lambda m, t: m.decay_r_squared >= t,
    ),
    "max_gc_content_diff": Check(
        config_field="max_gc_content_diff",
        result_field="per_base_composition",
        predicate=lambda m, t: _gc_max_diff(
            m.a_percentage,
            m.t_percentage,
            m.c_percentage,
            m.g_percentage,
        ) <= t
    )
}

def evaluate(result: QCResult, config: ThresholdConfig) -> dict[str, CheckStatus]:
    checks: dict[str, CheckStatus] = {}
    for name, check in _CHECKS.items():
        # TODO: Check out getattr, super cool use here
        thresholds = getattr(config, check.config_field)
        metric     = getattr(result, check.result_field)
        if thresholds is None or metric is None:
            continue
        if not check.predicate(metric, thresholds.fail):
            checks[name] = CheckStatus.FAIL
        elif not check.predicate(metric, thresholds.warn):
            checks[name] = CheckStatus.WARN
        else:
            checks[name] = CheckStatus.PASS
    return checks
