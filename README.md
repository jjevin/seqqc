# Seqqc - Single- or multi-file FASTQ quality analysis tool

## Overview

Seqqc is a FASTQ quality assessment CLI that is capable of evaluating
individual and bulk samples. Combining the per-read and aggregate
metrics of tools like FASTQC and MultiQC allows for streamlined
analysis, suitable for automated and distributed workflows.

## Installation

Seqqc uses pyproject for build management and installation.
To install Seqqc from source, clone this repository, navigate to
the home directory, and run the following:

```bash
pip install .
```

## Usage

After installation, run ```seqqc --help``` for available commands,
flags, and arguments.
