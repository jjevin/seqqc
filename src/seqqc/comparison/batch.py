import numpy as np
from seqqc.models.results import QCResult, SampleSummary, BatchSummary


def _extract_summary(result: QCResult) -> SampleSummary:
    """Pull scalar metrics from a QCResult into a flat summary"""
    mean_gc = None
    if result.per_read_gc is not None:
        mean_gc = result.per_read_gc.mean_gc

    mean_q = None
    if result.per_read_quality is not None:
        counts = np.array(result.per_read_quality.avg_qualities, dtype=float)
        total = counts.sum()
        if total > 0:
            mean_q = float(np.average(np.arange(len(counts)), weights=counts))

    max_n = None
    if result.per_base_composition is not None:
        max_n = max(result.per_base_composition.n_percentage)

    return SampleSummary(
        filename=result.filename,
        read_count=result.read_count.value if result.read_count else None,
        mean_quality=mean_q,
        mean_gc=mean_gc,
        max_n_fraction=max_n,
        decay_constant=(
            result.per_base_quality.decay_constant if result.per_base_quality else None
        ),
    )


def _flag_outliers(
    summaries: list[SampleSummary],
    z_threshold: float = 2.0,
) -> dict[str, list[str]]:
    """Flag samples whose scalar metrics deviate more than z_threshold std devs"""
    fields = [
        "read_count",
        "mean_quality",
        "mean_gc",
        "max_n_fraction",
        "decay_constant",
    ]
    flags: dict[str, list[str]] = {f: [] for f in fields}

    for field in fields:
        values = [
            (s.filename, getattr(s, field))
            for s in summaries
            if getattr(s, field) is not None
        ]
        if len(values) < 3:  # z-score is meaningless with fewer than 3 samples
            continue
        names, nums = zip(*values)
        arr = np.array(nums, dtype=float)
        mean, std = arr.mean(), arr.std()
        if std == 0:
            continue
        for name, val in zip(names, arr):
            if abs(val - mean) / std > z_threshold:
                flags[field].append(name)

    return {k: v for k, v in flags.items() if v}  # drop empty lists


def compute_batch_summary(results: list[QCResult]) -> BatchSummary:
    summaries = [_extract_summary(r) for r in results]
    return BatchSummary(
        samples=summaries,
        outlier_flags=_flag_outliers(summaries),
    )
