
# Test Dependencies

## Questa

Testcases require an installation of the Questa simulator, and for `vlog` & `vsim`
commands to be visible via the PATH environment variable.

*Questa - Intel FPGA Starter Edition* can be downloaded for free from Intel:
* Go to https://www.intel.com/content/www/us/en/collections/products/fpga/software/downloads.html?edition=pro&q=questa&s=Relevancy
* Select latest version of Questa
* Download Questa files.
* Install
    * Be sure to choose "Starter Edition" for the free version.
* Create an account on https://licensing.intel.com
    * press "Enroll" to register
    * After you confirm your email, go back to this page and press "Enroll" again to finish enrollment
* Go to https://licensing.intel.com/psg/s/sales-signup-evaluationlicenses
* Generate a free *Starter Edition* license file for Questa
    * Easiest to use a *fixed* license using your NIC ID (MAC address of your network card via `ifconfig`)
* Download the license file and point the `LM_LICENSE_FILE` environment variable to the folder which contains it.
* (optional) Delete Intel libraries to save some disk space
    * Delete `<install_dir>/questa_fse/intel`
    * Edit `<install_dir>/questa_fse/modelsim.ini` and remove lines that reference the `intel` libraries


## Vivado (optional)

To run synthesis tests, Vivado needs to be installed and visible via the PATH environment variable.

Vivado can be downloaded for free from: https://www.xilinx.com/support/download.html



## Python Packages
Install dependencies required for running tests

```bash
python3 -m pip install -r tests/requirements.txt
```



# Running tests

Tests can be launched from the test directory using `pytest`.
Use `pytest --workers auto` to run tests in parallel.

To run all tests:
```bash
python3 setup.py install
pytest tests
```

You can also run a specific testcase. For example:
```bash
pytest tests/test_hw_access
```

Command-line arguments can be used to explicitly select which simulator/synthesis tools are used
If unspecified, the tool will be selected automatically based on what you have installed.
```bash
pytest --sim-tool questa --synth-tool vivado
```


Alternatively, launch tests using the helper script. This handles installing
dependencies into a virtual environment automatically.
```bash
cd tests
./run.sh
```



# Test organization

The goal for this test infrastructure is to make it easy to add small-standalone
testcases, with minimal repetition/boilerplate code that is usually present in
SystemVerilog testbenches.

To accomplish this, Jinja templates are used extensively to generate the
resulting `tb.sv` file, as well as assist in dynamic testcase parameterization.



## CPU Interfaces
Each CPU interface type is described in its own folder as follows:

`lib/cpuifs/<type>/__init__.py`
: Definitions for CPU Interface test mode classes.

`lib/cpuifs/<type>/tb_inst.sv`
: Jinja template that defines how the CPU interface is declared & instantiated in the testbench file.

`lib/cpuifs/<type>/*.sv`
: Any other files required for compilation.



## Testcase
Each testcase group has its own folder and contains the following:

`test_*/__init__.py`
: Empty file required for test discovery.

`test_*/regblock.rdl`
: Testcase RDL file. Testcase infrastructure will automatically compile this and generate the regblock output SystemVerilog.

`test_*/tb_template.sv`
: Jinja template that defines the testcase-specific sequence.

`test_*/testcase.py`
: Defines Python unittest testcase entry point.



## Parameterization
Testcase classes can be parameterized using the [parameterized](https://github.com/wolever/parameterized) extension. This allows the same testcase to be run against multiple permutations of regblock export modes such as CPU interfaces, retiming flop stages, or even RDL parameterizations.
