from __future__ import annotations  # lazy import evaluation?
from abc import ABC, abstractmethod
from typing import ClassVar

from seqqc.parsers.fastq import Read
from seqqc.models.results import MetricResult

class MetricCalculator(ABC):
    # Each subclass declares which QCResult field it popualtes
    # ClassVar signals this belongs to the class, not instances
    result_field: ClassVar[str]

    @abstractmethod
    def update(self, read: Read) -> None:
        """Processing a single read, updating this class' internal state"""
        ... # TODO: best to use "..." instead of pass?

    @abstractmethod
    def finalize(self) -> MetricResult:
        """Return a completed metric result after all reads are processed"""
        ...
