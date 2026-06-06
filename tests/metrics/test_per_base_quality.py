import numpy as np
import pytest
from pathlib import Path

from seqqc.parsers.fastq import Read, read_fastq
from seqqc.metrics.per_base_quality import PerBaseQualityCalculator


def make_read(quality: list[int]) -> Read:
    return Read(
        name="test",
        sequence="A" * len(quality),
        quality=quality,
    )


class TestPerBaseQualityMedians:
    """Original median tests — behaviour unchanged after refactor."""

    def test_single_read_median_equals_own_scores(self):
        calc = PerBaseQualityCalculator()
        calc.update(make_read([30, 35, 40]))
        result = calc.finalize()
        assert result.medians == [30.0, 35.0, 40.0]

    def test_median_two_identical_reads(self):
        calc = PerBaseQualityCalculator()
        calc.update(make_read([20, 30]))
        calc.update(make_read([20, 30]))
        result = calc.finalize()
        assert result.medians == [20.0, 30.0]

    def test_median_two_different_reads(self):
        calc = PerBaseQualityCalculator()
        calc.update(make_read([10, 20]))
        calc.update(make_read([30, 40]))
        result = calc.finalize()
        assert result.medians == [20.0, 30.0]

    def test_median_test_file(self, simple_fastq_file: Path):
        calc = PerBaseQualityCalculator()
        for read in read_fastq(simple_fastq_file):
            calc.update(read)
        result = calc.finalize()
        assert result.medians == [20.0] * 4 + [40.0] * 4


class TestPerBaseQualityDecay:
    """Tests for the quality decay metric added in the refactor."""

    def test_flat_profile_returns_zero_decay(self):
        # max - min < 2 triggers early exit in _fit_decay.
        # Uniform quality is the expected case for high-quality short reads.
        calc = PerBaseQualityCalculator()
        for _ in range(50):
            calc.update(make_read([35] * 50))
        result = calc.finalize()
        assert result.decay_constant == 0.0
        assert result.decay_r_squared == 0.0

    def test_decaying_profile_returns_positive_lambda(self):
        # Quality scores that follow Q0 * exp(-λx) closely.
        # Using enough reads to make the medians stable.
        decaying = [int(40 * np.exp(-0.05 * i)) for i in range(30)]
        calc = PerBaseQualityCalculator()
        for _ in range(200):
            calc.update(make_read(decaying))
        result = calc.finalize()
        assert result.decay_constant > 0, "Decaying profile should have λ > 0"
        assert result.decay_r_squared > 0.8, "Exponential should fit well"

    def test_decaying_profile_initial_quality_near_max(self):
        # Q0 should be close to the quality at the start of the read.
        decaying = [int(40 * np.exp(-0.05 * i)) for i in range(30)]
        calc = PerBaseQualityCalculator()
        for _ in range(200):
            calc.update(make_read(decaying))
        result = calc.finalize()
        assert pytest.approx(result.decay_initial_quality, abs=3.0) == 40.0

    def test_decay_fields_are_always_present(self):
        # finalize() should always populate decay fields, even for short inputs.
        calc = PerBaseQualityCalculator()
        calc.update(make_read([30, 35, 40]))
        result = calc.finalize()
        assert isinstance(result.decay_constant, float)
        assert isinstance(result.decay_initial_quality, float)
        assert isinstance(result.decay_r_squared, float)

    def test_r_squared_bounded(self):
        # R² should always be in [0, 1] when the fit converges.
        decaying = [int(38 * np.exp(-0.03 * i)) for i in range(50)]
        calc = PerBaseQualityCalculator()
        for _ in range(100):
            calc.update(make_read(decaying))
        result = calc.finalize()
        assert 0.0 <= result.decay_r_squared <= 1.0


class TestPerBaseQualityOtherMetrics:
    """Spot-checks for quartile and mean metrics."""

    def test_mean_of_uniform_quality(self):
        calc = PerBaseQualityCalculator()
        for _ in range(10):
            calc.update(make_read([30] * 5))
        result = calc.finalize()
        assert result.means == pytest.approx([30.0] * 5)

    def test_quartiles_with_known_distribution(self):
        # Feed 100 reads at Q10 and 100 at Q30 at every position.
        # Q1 should be Q10, median should be between, Q3 should be Q30.
        calc = PerBaseQualityCalculator()
        for _ in range(100):
            calc.update(make_read([10] * 4))
            calc.update(make_read([30] * 4))
        result = calc.finalize()
        for q1 in result.first_quartiles:
            assert q1 == pytest.approx(10.0, abs=1.0)
        for q3 in result.third_quartiles:
            assert q3 == pytest.approx(30.0, abs=1.0)

    def test_variable_length_reads_correct_position_count(self):
        calc = PerBaseQualityCalculator()
        calc.update(make_read([40]))
        calc.update(make_read([40, 20]))
        result = calc.finalize()
        assert len(result.medians) == 2
        assert result.medians[1] == pytest.approx(20.0, abs=1.0)
