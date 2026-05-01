from pathlib import Path
from seqqc.parsers.fastq import read_fastq
from seqqc.metrics.read_count import ReadCountCalculator
from seqqc.models.results import QCResult

def analyze(path: Path) -> QCResult:
    calculators = [
        ReadCountCalculator(),
        # TODO: Future calculators added here
    ]

    for read in read_fastq(path):
        for calc in calculators:
            calc.update(read)

    # TODO: Need to update long term
    return QCResult(
        filename=path.name,
        read_count=calculators[0].finalize(),
    )

