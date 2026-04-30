import pytest
from pathlib import Path
from seqqc.parsers.fastq import Read, _decode_quality, read_fastq

# Read dataclass tests

class TestRead:
    def test_stores_field_correctly(self):
        read = Read(name="r1", sequence="ACGT", quality=[40, 40, 40, 40])
        assert read.name == "r1"
        assert read.sequence == "ACGT"
        assert read.quality == [40, 40, 40, 40]

    def test_rejects_mismatched_lengths(self):
        with pytest.raises(ValueError, match="does not match quality length"):
            Read(name="bad", sequence="ACGT", quality=[40, 40])

    def test_accepts_empty_sequence(self):
        # Edge case for accepting empty results (possible after trimming)
        read = Read(name="empty", sequence="", quality=[])
        assert read.sequence == ""


# _decode_quality tests

class TestDecodeQuality:
    @pytest.mark.parametrize("ascii_char, expected", [
        ("!", 0),  # minimum Phred score
        ("5", 20), # Q20 - 1% error probability
        ("I", 40), # Q40 - 0.01% error probability
        ("K", 42), # Illumina practical maximum
    ])
    def test_single_character_decoding(self, ascii_char: str, expected: int):
        assert _decode_quality(ascii_char) == [expected]

    def test_decodes_full_quality_string(self):
        assert _decode_quality("IIII") == [40, 40, 40, 40]

    def test_strips_trailing_newline(self):
        assert _decode_quality("II\n") == [40, 40]

    def test_empty_string_returns_empty_list(self):
        assert _decode_quality("") == []

        
# read_fastq generator tests

class TestReadFastq:
    def test_yields_correct_number_of_reads(self, simple_fastq_file: Path):
        reads = list(read_fastq(simple_fastq_file))
        assert len(reads) == 2

    def test_first_read(self, simple_fastq_file: Path):
        reads = list(read_fastq(simple_fastq_file))
        assert reads[0].name == "read_1"
        assert reads[0].sequence == "ACGTACGT"
        assert reads[0].quality == [40] * 8

    def test_yields_read_objects(self, single_read_file: Path):
        reads = list(read_fastq(single_read_file))
        assert all(isinstance(r, Read) for r in reads)
