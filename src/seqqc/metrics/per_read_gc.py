import numpy as np
from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerReadGCResult

class PerReadGCCalculator(MetricCalculator):
    result_field: ClassVar[str] = "per_read_gc"

    def __init__(self) -> None:
        # Indexed 0-100, each cell count represents the number of reads with that
        # GC percent
        self._distribution: np.ndarray = np.zeros(101, dtype=np.int64)

    def update(self, read: Read) -> None:
        # Skip empty reads
        if not read.sequence:
            return
        gc_count = read.sequence.count("G") + read.sequence.count("C")
        percent_gc = round(100 * gc_count / len(read.sequence))
        self._distribution[percent_gc] += 1

    def finalize(self) -> PerReadGCResult:
        total_gc = self._distribution.sum()
        return PerReadGCResult(
            gc_distribution=self._distribution.tolist(),
            mean_gc=float(
                np.average(np.arange(101), weights=self._distribution)
            ) if total_gc > 0 else 0.0
        )
