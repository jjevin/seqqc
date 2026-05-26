from pathlib import Path

from seqqc.parsers.fastq import read_fastq
from seqqc.metrics.base import MetricCalculator
from seqqc.metrics.read_count import ReadCountCalculator
from seqqc.metrics.per_base_quality import PerBaseQualityCalculator
from seqqc.metrics.per_base_composition import PerBaseCompositionCalculator
from seqqc.models.results import QCResult
from seqqc.rendering.html import render_report

_default_calculators: list[MetricCalculator] = [
    ReadCountCalculator(),
    PerBaseQualityCalculator(),
    PerBaseCompositionCalculator()
]

def analyze(
    path: Path, 
    output: Path,
    calculators: list[MetricCalculator] = _default_calculators
) -> QCResult:
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

