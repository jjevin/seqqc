from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import ReadCountResult

class ReadCountCalculator(MetricCalculator):

    def __init__(self) -> None:
        self._count: int = 0
    
    def update(self, read: Read) -> None:
        """Simple test for just incrementing a value with each read"""
        self._count += 1

    def finalize(self) -> ReadCountResult:
        """Returning a pydantic dump of metric results"""
        return ReadCountResult(value=self._count)
