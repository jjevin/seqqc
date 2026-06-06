import warnings
import numpy as np
from dataclasses import dataclass
from scipy.optimize import curve_fit, OptimizeWarning
from typing import ClassVar

from seqqc.metrics.base import MetricCalculator
from seqqc.parsers.fastq import Read
from seqqc.models.results import PerBaseQualityResult
    
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

    def _compute_metrics(self) -> dict[str, list[float]]:
        """Compute all per-position metrics in a single histogram pass.
        Dict keys match PerBaseQualityResult field names for unpacking."""
        n    = len(self._histograms)
        bins = np.arange(self._MAX_PHRED + 1)

        # TODO: Instantiate as zeroes, versus appending in loop?
        first_deciles   = [0.0] * n
        first_quartiles = [0.0] * n
        medians         = [0.0] * n
        third_quartiles = [0.0] * n
        ninth_deciles   = [0.0] * n
        means           = [0.0] * n

        for i, hist in enumerate(self._histograms):
            if hist.sum() == 0:
                continue
            first_deciles[i]   = self._quantile_from_histogram(hist, 0.10)
            first_quartiles[i] = self._quantile_from_histogram(hist, 0.25)
            medians[i]         = self._quantile_from_histogram(hist, 0.50)
            third_quartiles[i] = self._quantile_from_histogram(hist, 0.75)
            ninth_deciles[i]   = self._quantile_from_histogram(hist, 0.90)
            means[i]           = float(np.average(bins, weights=hist))

        return {
            "first_deciles":   first_deciles,
            "first_quartiles": first_quartiles,
            "medians":         medians,
            "third_quartiles": third_quartiles,
            "ninth_deciles":   ninth_deciles,
            "means":           means,
        }
            
    @staticmethod
    def _fit_decay(medians: list[float]) -> tuple[float, float, float]:
        """Fit Q(x) = Q_0 * exp(lambda * x) to per-position median quality scores.
        Returns (Q_0, decay constant lambda, R^2).
        If profile is too flat, returns (mean, 0.0, 0.0) as default"""
        
        y = np.array(medians, dtype=float)
        x = np.arange(len(y), dtype=float)

        # Guard: if the quality range is less that 2 Phred units, an exponential
        # model is unlikely to fit; meaning lambda ~= 0, no fitting needed
        if y.max() - y.min() < 2.0:
            return float(y.mean()), 0.0, 0.0

        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("error", category=OptimizeWarning)
                params, _ = curve_fit(
                    # Initial guess: Q_0 at first position, small decay
                    lambda x, q0, lam: q0 * np.exp(-lam * x),
                    x, y,
                    p0=[float(y.max()), 0.01],
                    maxfev=2000
                )
            q0, lam = params
            y_pred = q0 * np.exp(-lam * x)
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
            return float(q0), float(lam), float(r_squared)
        
        except (RuntimeError, OptimizeWarning):
            # RuntimeError: maxfex reached w/o convergence
            # OptimizeWarning: Covariance matrix could not be estimated -> degenerate fit
            return float(y.mean()), 0.0, 0.0

    def finalize(self) -> PerBaseQualityResult:
        data = self._compute_metrics()
        q0, lam, r_squared = self._fit_decay(data["medians"])

        return PerBaseQualityResult(
            **data,
            decay_initial_quality=q0,
            decay_constant=lam,
            decay_r_squared=r_squared,
        )
        
