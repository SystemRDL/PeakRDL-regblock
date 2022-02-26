#!/bin/bash

set -e

this_dir="$( cd "$(dirname "$0")" ; pwd -P )"

# Initialize venv
venv_bin=$this_dir/.venv/bin
python3 -m venv $this_dir/.venv
source $this_dir/.venv/bin/activate

# Install test dependencies
pip install -U pip setuptools wheel
pip install -r $this_dir/requirements.txt

# Install dut
cd $this_dir/../
python $this_dir/../setup.py install
cd $this_dir

# Run unit tests
export SKIP_SYNTH_TESTS=1
pytest --workers auto

# Run lint
pylint --rcfile $this_dir/pylint.rc ../peakrdl

# Run static type checking
mypy $this_dir/../peakrdl
