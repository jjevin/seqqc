import numpy as np
from dataclasses import dataclass
from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerBaseQualityResult

@dataclass
class _HistogramMetrics:
    first_decile:   float
    first_quartile: float
    median:         float
    third_quartile: float
    ninth_decile:   float
    mean:           float
    
class PerBaseQualityCalculator(MetricCalculator):
    result_field: ClassVar[str] = "per_base_quality"

    # Illumina Phred scores run from 0-42
    # Using this to create a histogram for our median calculations
    _MAX_PHRED: int = 42
    
    def __init__(self) -> None:
        self._histograms: list[np.ndarray] = []

    def _ensure_capacity(self, length: int) -> None:
        """Extend the histogram to cover positions up to 'length'"""
        while len(self._histograms) < length:
            self._histograms.append(
                np.zeros(self._MAX_PHRED + 1, dtype=int)
            )

    def update(self, read: Read) -> None:
        self._ensure_capacity(len(read.quality))
        for pos, score in enumerate(read.quality):
            # TODO: Not sure if clamped is needed?
            clamped = min(score, self._MAX_PHRED)
            self._histograms[pos][clamped] += 1

    @staticmethod
    def _quantile_from_histogram(hist: np.ndarray, q:float) -> float:
        """Compute quantile q from a histogram via CDF interpolation"""
        # h is the fractional index of the virtual sorted observation array
        # This matches numpy's 'linear' interpolation method for np.quantile
        # See https://numpy.org/doc/stable/reference/generated/numpy.quantile.html
        total = hist.sum()
        h = q * (total - 1)
        floor_h = int(np.floor(h))
        ceil_h = min(int(np.ceil(h)), int(total)-1)
        frac = h - floor_h

        cumsum = np.cumsum(hist)

        # Find which bin contains the floor and ceiling of observations
        # side='right' gives the first bin where cumsum exceeds the index
        low_bin  = min(int(np.searchsorted(cumsum, floor_h, side='right')), len(hist) - 1)
        high_bin = min(int(np.searchsorted(cumsum, ceil_h, side='right')), len(hist) - 1)

        return low_bin + frac * (high_bin - low_bin)

    def _metrics_from_histogram(self, hist: np.ndarray) -> _HistogramMetrics:
        if hist.sum() == 0:
            return  _HistogramMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        bins = np.arange(len(hist))
        mean = float(np.average(bins, weights=hist))

        return _HistogramMetrics(
            first_decile   = self._quantile_from_histogram(hist, 0.10),
            first_quartile = self._quantile_from_histogram(hist, 0.25),
            median         = self._quantile_from_histogram(hist, 0.50),
            third_quartile = self._quantile_from_histogram(hist, 0.75),
            ninth_decile   = self._quantile_from_histogram(hist, 0.90),
            mean           = mean,
        )

    def finalize(self) -> PerBaseQualityResult:
        """Returning a pydantic dump of metric results"""
        metrics = [
            self._metrics_from_histogram(h) for h in self._histograms
        ]
        # TODO: Change the result dataclass to be a singleton that appends instead?
        return PerBaseQualityResult(
            first_deciles   = [metric.first_decile   for metric in metrics],
            first_quartiles = [metric.first_quartile for metric in metrics],
            medians         = [metric.median         for metric in metrics],
            third_quartiles = [metric.third_quartile for metric in metrics],
            ninth_deciles   = [metric.ninth_decile   for metric in metrics],
            means           = [metric.mean           for metric in metrics]
        )
