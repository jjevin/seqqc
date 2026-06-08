from pathlib import Path

from seqqc.parsers.fastq import read_fastq
from seqqc.metrics.base import MetricCalculator
from seqqc.metrics.read_count import ReadCountCalculator
from seqqc.metrics.per_base_quality import PerBaseQualityCalculator
from seqqc.metrics.per_base_composition import PerBaseCompositionCalculator
from seqqc.metrics.per_read_quality import PerReadQualityCalculator
from seqqc.metrics.per_read_length import PerReadLengthCalculator
from seqqc.metrics.per_read_gc import PerReadGCCalculator
from seqqc.models.results import QCResult
from seqqc.rendering.html import render_report
from seqqc.thresholds.schema import ThresholdConfig

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
    json_path: Path | None = None,
    calculators: list[MetricCalculator] | None = None,
    threshold_config: ThresholdConfig | None = None,
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
    result = QCResult(filename=path.name, **metric_results)

    if threshold_config is not None:
        from seqqc.thresholds.evaluator import evaluate
        from seqqc.models.results import EvaluationResult
        # TODO: Look up Pydantic model copy logic
        result = result.model_copy(
            update = {
                "evaluation": EvaluationResult(
                    checks=evaluate(result, threshold_config)
                )
            }
        )

    render_report(result, output, threshold_config)

    if json_path is not None:
        json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
        
    return result

