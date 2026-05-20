import numpy as np
from dataclasses import dataclass

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerBaseQualityResult

@dataclass
class _HistogramMetrics():
    first_decile:   float
    first_quartile: float
    median: 	    float
    third_quartile: float
    ninth_decile:   float
    mean:	    float

class PerBaseQualityCalculator(MetricCalculator):

    # Illumina Phred scores run from 0-42
    # Using this to create a histogram for our median calculations
    _MAX_PHRED: int = 42
    
    def __init__(self) -> None:
        # TODO: np.ndarray? 
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

    # TODO: This currently loads the entire set of reads for a lane in memory.
    # Better than base case (all reads for all lanes), but worse than using the
    # histogram directly. Try refactoring to not use the scores array.
    def _metrics_from_histogram(self, hist: np.ndarray) -> float:
        bins = list(range(self._MAX_PHRED + 1))
        scores = np.array(np.repeat(bins, hist))
        return _HistogramMetrics(
            # TODO: See about different quantile estimation methods
            np.quantile(scores, 0.10),
            np.quantile(scores, 0.25),
            np.quantile(scores, 0.50),
            np.quantile(scores, 0.75),
            np.quantile(scores, 0.90),
            np.mean(scores)
        )

    def finalize(self) -> PerBaseQualityResult:
        """Returning a pydantic dump of metric results"""
        metrics = [
            self._metrics_from_histogram(h) for h in self._histograms
        ]
        # TODO: Change the result dataclass to be a singleton that appends instead?
        return PerBaseQualityResult(
            per_position_medians=[metric.median for metric in metrics]
    	)
