import numpy as np
from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerBaseCompositionResult

class PerBaseCompositionCalculator(MetricCalculator):
    result_field: ClassVar[str] = "per_base_composition"

    # Base N used as default when confidence is low
    _comp = np.dtype([
        ('A', 'i4'), 
        ('T', 'i4'), 
        ('G', 'i4'), 
        ('C', 'i4'),
        ('N', 'i4'),
        ('Total', 'i4')
    ])

    def __init__(self) -> None:
        self._composition: np.ndarray = np.ndarray(0, dtype=self._comp)

    def _ensure_capacity(self, length: int) -> None:
        """Extend composition array to cover positions up to 'length'"""
        if len(self._composition) < length:
            length_diff = length - len(self._composition)
            self._composition = np.append(
                self._composition,
                np.zeros(length_diff, dtype=self._comp)
            )

    def update(self, read: Read) -> None:
        self._ensure_capacity(len(read.sequence))
        for pos, base in enumerate(read.sequence):
            self._composition[pos][base] += 1
            self._composition[pos]['Total'] += 1

    def finalize(self) -> PerBaseCompositionResult:
        return PerBaseCompositionResult(
            a_percentage=(self._composition['A']/self._composition['Total']).tolist(),
            t_percentage=(self._composition['T']/self._composition['Total']).tolist(),
            g_percentage=(self._composition['G']/self._composition['Total']).tolist(),
            c_percentage=(self._composition['C']/self._composition['Total']).tolist(),
            n_percentage=(self._composition['N']/self._composition['Total']).tolist(),
        )

