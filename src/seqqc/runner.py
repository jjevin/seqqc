from pathlib import Path
from seqqc.parsers.fastq import read_fastq
from seqqc.metrics.read_count import ReadCountCalculator
from seqqc.metrics.per_base_quality import PerBaseQualityCalculator
from seqqc.models.results import QCResult

def analyze(path: Path) -> QCResult:
    calculators = [
        ReadCountCalculator(),
        PerBaseQualityCalculator()
        # TODO: Future calculators added here
    ]

    for read in read_fastq(path):
        for calc in calculators:
            calc.update(read)

    # TODO: Need to update long term
    return QCResult(
        filename=path.name,
        read_count=calculators[0].finalize()
        ,per_base_quality=calculators[1].finalize()
    )

