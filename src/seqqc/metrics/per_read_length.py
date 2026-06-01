from collections import Counter
import numpy as np
from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerReadLengthResult

class PerReadLengthCalculator(MetricCalculator):
    result_field: ClassVar[str] = "per_read_length"

    def __init__(self) -> None:
        self._length_counter: Counter = Counter([])

    def update(self, read: Read) -> None:
        self._length_counter.update([len(read.sequence)])

    def finalize(self) -> PerReadLengthResult:
        lengths = np.array(list(self._length_counter.keys()),   dtype=np.int64)
        counts  = np.array(list(self._length_counter.values()), dtype=np.int64)
        total   = counts.sum()

        weighted_mean    = float(np.average(lengths, weights=counts))
        # Count has no guaranteed order, which is needed for cumsum
        sorted_lengths   = np.sort(lengths)
        sorted_counts    = counts[np.argsort(lengths)]
        # Median calculation from cumulative sum
        cumulative       = np.cumsum(sorted_counts)
        median_Length    = float(sorted_lengths[np.searchsorted(cumulative, total / 2)])
        # N50 calculation
        half_total_bases = (sorted_lengths * sorted_counts).sum() / 2
        base_cumsum      = np.cumsum(sorted_lengths * sorted_counts)
        n50              = int(sorted_lengths[np.searchsorted(base_cumsum, half_total_bases)])
        
        return PerReadLengthResult(
            length_distribution=dict(self._length_counter),
            mean=weighted_mean,
            median=median_Length,
            n50=n50,
        )
