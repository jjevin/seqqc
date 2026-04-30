import pytest
from pathlib import Path

SIMPLE_FASTQ_CONTENT = "\n".join([
    "@read_1",
    "ACGTACGT",
    "+",
    "IIIIIIII",
    "@read_2",
    "NNNN",
    "+",
    "!!!!"
])

@pytest.fixture
def simple_fastq_file(tmp_path: Path) -> Path:
    """A valid FASTQ file with three reads of known properties"""
    path = tmp_path / "simple.fastq"
    path.write_text(SIMPLE_FASTQ_CONTENT)
    return path

@pytest.fixture
def single_read_file(tmp_path: Path) -> Path:
    """A FASTQ file containing exactly one read"""
    content = "\n".join(["@solo", "ACGT", "+", "IIII"])
    path = tmp_path / "simple.fastq"
    path.write_text(content)
    return path
