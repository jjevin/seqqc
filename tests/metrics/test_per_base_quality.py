import pytest
from pathlib import Path
from seqqc.parsers.fastq import Read, read_fastq
from seqqc.metrics.per_base_quality import PerBaseQualityCalculator

def make_read(quality: list[int]) -> Read:
    return Read(
        name="test",
        sequence="A" * len(quality),
        quality=quality
    )

class TestPerBaseQuality:

    def test_single_read_median_equals_own_scores(self):
        per_base_quality = PerBaseQualityCalculator()
        per_base_quality.update(make_read([30, 35, 40]))
        result = per_base_quality.finalize()
        assert result.per_position_medians == [30.0, 35.0, 40.0]

    def test_median_two_identical_reads(self):
        per_base_quality = PerBaseQualityCalculator()
        per_base_quality.update(make_read([20, 30]))
        per_base_quality.update(make_read([20, 30]))
        result = per_base_quality.finalize()
        assert result.per_position_medians == [20.0, 30.0]

    def test_median_two_different_reads(self):
        per_base_quality = PerBaseQualityCalculator()
        per_base_quality.update(make_read([10, 20]))
        per_base_quality.update(make_read([30, 40]))
        result = per_base_quality.finalize()
        assert result.per_position_medians == [20.0, 30.0]

    def test_median_test_file(self, simple_fastq_file: Path):
        per_base_quality = PerBaseQualityCalculator()
        reads = list(read_fastq(simple_fastq_file))
        for r in reads:
            per_base_quality.update(r)
        result = per_base_quality.finalize()
        assert result.per_position_medians == [20] * 4 + [40] * 4
            
