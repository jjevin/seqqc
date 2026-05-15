import pytest
from pathlib import Path
from seqqc.parsers.fastq import Read
from seqqc.metrics.read_count import ReadCountCalculator

class TestReadCount:
    def test_read_count_zero(self):
        read_count = ReadCountCalculator()
        result = read_count.finalize()
        assert result.value == 0

    def test_read_count_ten(self):
        read_count = ReadCountCalculator()
        read = Read('Test', '', [])
        for _ in range(10): read_count.update(read)
        result = read_count.finalize()
        assert result.value == 10

    def test_read_count_dump(self):
        read_count = ReadCountCalculator()
        result = read_count.finalize()
        print(result.model_dump_json())
        assert result.model_dump_json() == '{"metric_name":"read_count","value":0}'
        
        
