
ModelSim
--------

Testcases require an installation of ModelSim/QuestaSim, and for `vlog` & `vsim`
commands to be visible via the PATH environment variable.

ModelSim - Intel FPGA Edition can be downloaded for free from https://fpgasoftware.intel.com/ and is sufficient to run unit tests.

Running tests
-------------

```
cd test/
python3 -m pip install requirements.txt
pytest -n auto
```
