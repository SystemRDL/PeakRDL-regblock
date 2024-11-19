from typing import Optional
import unittest
import os
import glob
import shutil
import inspect
import pathlib

import pytest
from systemrdl import RDLCompiler

from peakrdl_regblock_vhdl import RegblockExporter as VhdlRegblockExporter
from peakrdl_regblock import RegblockExporter as SvRegblockExporter
from peakrdl_regblock.udps import ALL_UDPS

from .vhdl_adapter import VhdlAdapter
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
    retime_external = False
    default_reset_activelow = False
    default_reset_async = False

    #: this gets auto-loaded via the _load_request autouse fixture
    request = None # type: pytest.FixtureRequest

    sv_exporter = SvRegblockExporter()
    vhdl_exporter = VhdlRegblockExporter()

    @pytest.fixture(autouse=True)
    def _load_request(self, request):
        self.request = request

    @property
    def rerun(self) -> bool:
        """
        Re-run wothout deleting and re-generating prior output directory.
        """
        return self.request.config.getoption("--rerun")

    def get_testcase_dir(self) -> str:
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        return class_dir

    def get_run_dir(self) -> str:
        this_dir = self.get_testcase_dir()
        run_dir = os.path.join(this_dir, "run.out", self.__class__.__name__)
        return run_dir

    def _write_params(self) -> None:
        """
        Write out the class parameters to a file so that it is easier to debug
        how a testcase was parameterized
        """
        path = os.path.join(self.get_run_dir(), "params.txt")

        with open(path, 'w') as f:
            for k, v in self.__class__.__dict__.items():
                if k.startswith("_") or callable(v):
                    continue
                f.write(f"{k}: {repr(v)}\n")


    def _export_regblock(self):
        """
        Call the peakrdl_regblock exporter to generate the DUT
        """
        this_dir = self.get_testcase_dir()

        if self.rdl_file:
            rdl_file = self.rdl_file
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
        root = rdlc.elaborate(self.rdl_elab_target, "regblock", self.rdl_elab_params)

        for lang, exporter, cpuif_cls in (
            ("sv", self.sv_exporter, self.cpuif.sv_cpuif_cls),
            ("vhdl", self.vhdl_exporter, self.cpuif.vhdl_cpuif_cls),
        ):
            exporter.export(
                root,
                self.get_run_dir(),
                module_name=lang+"_regblock",
                package_name=lang+"_regblock_pkg",
                cpuif_cls=cpuif_cls,
                retime_read_fanin=self.retime_read_fanin,
                retime_read_response=self.retime_read_response,
                reuse_hwif_typedefs=self.reuse_hwif_typedefs,
                retime_external_reg=self.retime_external,
                retime_external_regfile=self.retime_external,
                retime_external_mem=self.retime_external,
                retime_external_addrmap=self.retime_external,
                default_reset_activelow=self.default_reset_activelow,
                default_reset_async=self.default_reset_async,
            )
        vhdl_adapter = VhdlAdapter(self.sv_exporter, self.vhdl_exporter, self.cpuif)
        vhdl_adapter.export(self.get_run_dir())

    def setUp(self) -> None:
        if self.rerun:
            return

        # Create fresh build dir
        run_dir = self.get_run_dir()
        if os.path.exists(run_dir):
            shutil.rmtree(run_dir)
        pathlib.Path(run_dir).mkdir(parents=True, exist_ok=True)

        self._write_params()

        # Convert testcase RDL file --> SV
        self._export_regblock()
