from typing import Optional, List
import unittest
import os
import glob
import shutil
import inspect
import pathlib

import pytest
from systemrdl import RDLCompiler

from peakrdl_regblock import RegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

from .cpuifs.base import CpuifTestMode
from .cpuifs.apb4 import APB4


class BaseTestCase(unittest.TestCase):
    #: Path to the testcase's RDL file.
    #: Relative to the testcase's dir. If unset, the first RDL file found in the
    #: testcase dir will be used
    rdl_file = None # type: Optional[str]

    #: RDL type name to elaborate. If unset, compiler will automatically choose
    #: the top.
    rdl_elab_target = None # type: Optional[str]

    #: Parameters to pass into RDL elaboration
    rdl_elab_params = {}

    #: Define what CPUIF to use for this testcase
    cpuif = APB4() # type: CpuifTestMode

    # Other exporter args:
    retime_read_fanin = False
    retime_read_response = False
    reuse_hwif_typedefs = True

    #: this gets auto-loaded via the _load_request autouse fixture
    request = None # type: pytest.FixtureRequest

    exporter = RegblockExporter()

    @pytest.fixture(autouse=True)
    def _load_request(self, request):
        self.request = request

    @classmethod
    def get_testcase_dir(cls) -> str:
        class_dir = os.path.dirname(inspect.getfile(cls))
        return class_dir

    @classmethod
    def get_run_dir(cls) -> str:
        this_dir = cls.get_testcase_dir()
        run_dir = os.path.join(this_dir, "run.out", cls.__name__)
        return run_dir

    @classmethod
    def _write_params(cls) -> None:
        """
        Write out the class parameters to a file so that it is easier to debug
        how a testcase was parameterized
        """
        path = os.path.join(cls.get_run_dir(), "params.txt")

        with open(path, 'w') as f:
            for k, v in cls.__dict__.items():
                if k.startswith("_") or callable(v):
                    continue
                f.write(f"{k}: {repr(v)}\n")


    @classmethod
    def _export_regblock(cls):
        """
        Call the peakrdl_regblock exporter to generate the DUT
        """
        this_dir = cls.get_testcase_dir()

        if cls.rdl_file:
            rdl_file = cls.rdl_file
        else:
            # Find any *.rdl file in testcase dir
            rdl_file = glob.glob(os.path.join(this_dir, "*.rdl"))[0]

        rdlc = RDLCompiler()

        # Load the UDPs
        for udp in ALL_UDPS:
            rdlc.register_udp(udp)
        # ... including the definition
        udp_file = os.path.join(this_dir, "../../hdl-src/regblock_udps.rdl")
        rdlc.compile_file(udp_file)

        rdlc.compile_file(rdl_file)
        root = rdlc.elaborate(cls.rdl_elab_target, "regblock", cls.rdl_elab_params)

        cls.exporter.export(
            root,
            cls.get_run_dir(),
            module_name="regblock",
            package_name="regblock_pkg",
            cpuif_cls=cls.cpuif.cpuif_cls,
            retime_read_fanin=cls.retime_read_fanin,
            retime_read_response=cls.retime_read_response,
            reuse_hwif_typedefs=cls.reuse_hwif_typedefs
        )

    @classmethod
    def setUpClass(cls):
        # Create fresh build dir
        run_dir = cls.get_run_dir()
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        pathlib.Path(run_dir).mkdir(parents=True, exist_ok=True)

        cls._write_params()

        # Convert testcase RDL file --> SV
        cls._export_regblock()


    def setUp(self) -> None:
        # cd into the run directory
        self.original_cwd = os.getcwd()
        os.chdir(self.get_run_dir())


    def run_test(self, plusargs:List[str] = None) -> None:
        simulator = self.simulator_cls(testcase_cls_inst=self)
        simulator.run(plusargs)
