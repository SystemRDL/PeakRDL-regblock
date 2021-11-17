#!/bin/bash
set -e

../export.py test_regblock.rdl

vlog -sv -suppress 2720 -quiet -f src.f
vsim -c -quiet tb -do "log -r /*; run -all; exit;"
