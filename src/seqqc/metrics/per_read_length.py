from collections import Counter
from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerReadLengthResult

class PerReadLengthCalculator(MetricCalculator):
    result_field: ClassVar[str] = "per_read_length"

    def __init__(self) -> None:
        self._LengthCounter: Counter = Counter([])

    def update(self, read: Read) -> None:
        self._LengthCounter.update([len(read.sequence)])

    def finalize(self) -> PerReadLengthResult:
        return PerReadLengthResult(
            length_counter=self._LengthCounter
            #read_lengths = list(self._LengthCounter.elements())
        )
