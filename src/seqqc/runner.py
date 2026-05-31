from pathlib import Path

from seqqc.parsers.fastq import read_fastq
# TODO: Better just to import as import seqqc.metrics.*?
from seqqc.metrics.base import MetricCalculator
from seqqc.metrics.read_count import ReadCountCalculator
from seqqc.metrics.per_base_quality import PerBaseQualityCalculator
from seqqc.metrics.per_base_composition import PerBaseCompositionCalculator
from seqqc.metrics.per_read_quality import PerReadQualityCalculator
from seqqc.metrics.per_read_length import PerReadLengthCalculator
from seqqc.metrics.per_read_gc import PerReadGCCalculator
from seqqc.models.results import QCResult
from seqqc.rendering.html import render_report

# Necessary for clearing calculator instance when calling analyze() twice
def _default_calculators() -> list[MetricCalculator]:
    return [
        ReadCountCalculator(),
        PerBaseQualityCalculator(),
        PerBaseCompositionCalculator(),
        PerReadQualityCalculator(),
        PerReadLengthCalculator(),
        PerReadGCCalculator()
    ]

def analyze(
    path: Path, 
    output: Path,
    calculators: list[MetricCalculator] | None = None
) -> QCResult:
    if calculators is None:
        calculators = _default_calculators()
        
    for read in read_fastq(path):
        for calc in calculators:
            calc.update(read)

    metric_results = {
        calc.result_field: calc.finalize()
        for calc in calculators 
    }

    # TODO: Look into dictionary unpacking
    result = QCResult(filename=path.name, **metric_results)
    render_report(result, output)
    return result

