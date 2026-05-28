from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerReadQualityResult

class PerReadQualityCalculator(MetricCalculator):
    result_field: ClassVar[str] = "per_read_quality"

    def __init__(self) -> None:
        self._qualities: list[int] = [0] * 43

    def update(self, read: Read) -> None:
        avg_quality = sum(read.quality) / len(read.quality)
        self._qualities[round(avg_quality)] += 1

    def finalize(self) -> PerReadQualityResult:
        return PerReadQualityResult(
            avg_qualities = self._qualities
        )
