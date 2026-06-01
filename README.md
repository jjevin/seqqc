# Seqqc - Single- or multi-file FASTQ quality analysis tool

![CI](https://github.com/jjevin/seqqc/actions/workflows/ci.yml/badge.svg)

A Python CLI for FASTQ quality analysis. Design to complement [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) with native multi-sample batch comparison, JSON-first output, configurable pass/fail thresholds for pipeline integration, and a novel per-sample quality decay metric.

---

## Why seqqc?

FastQC is the standard for FASTQ quality control, but it has a few practical limitations that `seqqc` addresses:

|                         | FastQC            | seqqc                             |
|-------------------------|-------------------|-----------------------------------|
| Multi-sample comparison | Required MultiQC  | Native (`seqqc compare`)          |
| Machine-readable output | HTML only         | JSON-first, HTML report optional  |
| Pipeline integration    | Manual inspection | Configurable pass/fail exit codes |
| Quality decay metric    | Visual only       | Quantified decay constant         |
| Extensibility           | Closed (Java)     | Open plugin achitecture (Python)  |

--- 

## Installation

`seqqc` is still prerelease. If you are interested in trying it out, please build the project from source:

```bash
git clone https://github.com/jjevin/seqqc.git
cd seqqc
pip install -e .
```

Requires Python >= 3.11

--- 

## Quick Start

``` bash
# Analyze a single FASTQ file
seqqc run sample.fastq.gz

# Specify output path
seqqc run sample.fast.gz --output reports/sample_report.html

# Compare multiple files (coming soon)
seqqc compare sample1.fastq.gz sample2.fastq.gz --output batch_report.html
```

A sample report generated from a small test dataset is available at [`examples/sample_report.html`](examples/sample_report.html).

---

## Current Status

`seqqc` is under active development. Please refer to the table below to track implementation status by command and metric:

### `seqqc run` - Single-file analysis 

| Metric                        | Status   | Notes                                                 |
|-------------------------------|----------|-------------------------------------------------------|
| Read Count                    | Complete |                                                       |
| Per-base quality scores       | Complete | Median, mean, Q1/Q3, P10/P90 per position             |
| Per-base sequence composition | Complete | A/T/G/C fraction per position with deviation shading  |
| Per-base N content            | Complete | Derived from composition; pass/warn/fail bands        |
| Per-read mean quality         | Complete | Histogram of mean Phred quality scores per read       |
| Per-read length distribution  | Complete | N50, median, mean; variable- and zero-length warnings |
| Per-read GC content           | Complete | Observed vs. theoretical / normal distribution        |
| Sequence duplication rate     | Planned  | Hash-based estimation                                 |
| Adapter contamination         | Planned  | Common Illumina adapter sequences                     |
| Overrepresented sequences     | Planned  | K-mer frequency analysis                              |
| Quality decay rate            | Planned  | Fitted exponential decay constant                     |

### `seqqc compare` - Multi-file analysis

| Feature                           | Status  | Notes                                               |
|-----------------------------------|---------|-----------------------------------------------------|
| Batch report gneration            | Planned | Combined HTML report for N Samples                  |
| Cross-sample outlier detection    | Planned | Flag samples 2+ standard deviations from batch mean |
| Configurable pass/fail thresholds | Planned | YAML config, pipline-compatible exit codes          |


### Output formats

| Format                  | Status      | Notes                                          |
|-------------------------|-------------|------------------------------------------------|
| Interactive HTML report | Complete    | Self-contained, using Plotly for visualization |
| JSON output             | In progress | Using Pydantic for JSON encoding               |
| Terminal summary        | Planned     | Using `rich` for rich text output              |

--- 

## Acknowledgements

Quality threshold defauls and metric definitions follow [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) by Simon Andrews at the Babraham Institute. Test data sourced from the [Genome in a Bottle](https://www.nist.gov/programs-biophotonics/genome-bottle) project.
