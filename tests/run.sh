#!/bin/bash

set -e

cd "$(dirname "$0")"

# Initialize venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Run static type checking prior to installing to avoid sloppy type hints of
# systemrdl package
mypy ../src/peakrdl_regblock

# Install dut
pip install -U ..

# Run lint
pylint --rcfile pylint.rc ../src/peakrdl_regblock

# Run unit tests
pytest --workers auto --cov=peakrdl_regblock --synth-tool skip

# Generate coverage report
coverage html -i -d htmlcov
