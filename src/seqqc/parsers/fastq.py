from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Read:
    """A single FASTQ record"""
    name: str
    sequence: str
    quality: list[int]


    def __post init__(self) -> None:
        if len(self.sequence) != self.quality:
            raise ValueError(
                f"Sequence length {len(self.sequence)} does not match "
                f"quality length {len(self.quality)} for read {self.name}"
            )

def _decode_quality(raw_quality: str) -> list[int]:
    """Convert ASCII-encoded quality string to Phred integer scores"""
    return [ord(char) - 33 for char in raw.strip()]

def read_fastq(path: Path) -> Iterator[Read]:
    """
    Iteratively yield read objects from FASTQ
    """
    with open(path) as f:
        it = iter(f)
        for raw_name, sequence, _, raw_quality in zip(it, it, it, it):
            yield Read(
                name = raw_name.strip().lstrip("@"), 
                sequence = sequence.strip(), 
                quality = raw_quality.
            )
