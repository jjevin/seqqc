from __future__ import annotations  # lazy import evaluation?
from abc import ABC, abstractmethod
from seqqc.parsers.fastq import Read

class MetricCalculator(ABC):

    @abstractmethod
    def update(self, read: Read) -> None:
        """Processing a single read, updating this class' internal state"""
        ... # best to use "..." instead of pass?

    @abstractmethod
    def finalize(self) -> MetricResult:
        """Return a completed metric result after all reads are processed"""
        ...
