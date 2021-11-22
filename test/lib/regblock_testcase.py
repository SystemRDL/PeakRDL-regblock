from typing import Optional, List
import unittest
import os
import glob
import shutil
import subprocess
import inspect

import pytest
import jinja2 as jj
from systemrdl import RDLCompiler

from peakrdl.regblock import RegblockExporter
from .cpuifs.base import CpuifTestMode
from .cpuifs.apb3 import APB3


class RegblockTestCase(unittest.TestCase):
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
    cpuif = APB3() # type: CpuifTestMode

    # Other exporter args:
    retime_read_fanin = False
    retime_read_response = False

    #: Abort test if it exceeds this number of clock cycles
    timeout_clk_cycles = 1000

    #: this gets auto-loaded via the _load_request autouse fixture
    request = None # type: pytest.FixtureRequest

    @pytest.fixture(autouse=True)
    def _load_request(self, request):
        self.request = request

    @classmethod
    def get_testcase_dir(cls) -> str:
        class_dir = os.path.dirname(inspect.getfile(cls))
        return class_dir

    @classmethod
    def get_build_dir(cls) -> str:
        this_dir = cls.get_testcase_dir()
        build_dir = os.path.join(this_dir, cls.__name__ + ".out")
        return build_dir

    @classmethod
    def _write_params(cls) -> None:
        """
        Write out the class parameters to a file so that it is easier to debug
        how a testcase was parameterized
        """
        path = os.path.join(cls.get_build_dir(), "params.txt")

        with open(path, 'w') as f:
            for k, v in cls.__dict__.items():
                if k.startswith("_") or callable(v):
                    continue
                f.write(f"{k}: {repr(v)}\n")


    @classmethod
    def _export_regblock(cls) -> RegblockExporter:
        """
        Call the peakrdl.regblock exporter to generate the DUT
        """
        this_dir = cls.get_testcase_dir()

        if cls.rdl_file:
            rdl_file = cls.rdl_file
        else:
            # Find any *.rdl file in testcase dir
            rdl_file = glob.glob(os.path.join(this_dir, "*.rdl"))[0]

        rdlc = RDLCompiler()
        rdlc.compile_file(rdl_file)
        root = rdlc.elaborate(cls.rdl_elab_target, "regblock", cls.rdl_elab_params)

        exporter = RegblockExporter()
        exporter.export(
            root,
            cls.get_build_dir(),
            module_name="regblock",
            package_name="regblock_pkg",
            cpuif_cls=cls.cpuif.cpuif_cls,
            retime_read_fanin=cls.retime_read_fanin,
            retime_read_response=cls.retime_read_response,
        )

        return exporter

    @classmethod
    def _generate_tb(cls, exporter: RegblockExporter):
        """
        Render the testbench template into actual tb.sv
        """
        template_root_path = os.path.join(os.path.dirname(__file__), "..")
        loader = jj.FileSystemLoader(
            template_root_path
        )
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
        )

        context = {
            "cls": cls,
            "exporter": exporter,
        }

        # template path needs to be relative to the Jinja loader root
        template_path = os.path.join(cls.get_testcase_dir(), "tb.sv")
        template_path = os.path.relpath(template_path, template_root_path)
        template = jj_env.get_template(template_path)

        output_path = os.path.join(cls.get_build_dir(), "tb.sv")
        stream = template.stream(context)
        stream.dump(output_path)


    @classmethod
    def _compile_tb(cls):
        # CD into the build directory
        cwd = os.getcwd()
        os.chdir(cls.get_build_dir())

        cmd = [
            "vlog", "-sv", "-quiet", "-l", "build.log",

            # Free version of ModelSim throws errors if generate/endgenerate
            # blocks are not used.
            # These have been made optional long ago. Modern versions of SystemVerilog do
            # not require them and I prefer not to add them.
            "-suppress", "2720",

            # Ignore noisy warning about vopt-time checking of always_comb/always_latch
            "-suppress", "2583",
        ]

        # Add CPUIF sources
        cmd.extend(cls.cpuif.get_tb_files())

        # Add DUT sources
        cmd.append("regblock_pkg.sv")
        cmd.append("regblock.sv")

        # Add TB
        cmd.append("tb.sv")

        # Run command!
        try:
            subprocess.run(cmd, check=True)
        finally:
            # cd back
            os.chdir(cwd)


    @classmethod
    def setUpClass(cls):
        # Create fresh build dir
        build_dir = cls.get_build_dir()
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        os.mkdir(build_dir)

        cls._write_params()

        # Convert testcase RDL file --> SV
        exporter = cls._export_regblock()

        # Create testbench from template
        cls._generate_tb(exporter)

        cls._compile_tb()


    def setUp(self) -> None:
        # cd into the build directory
        self.original_cwd = os.getcwd()
        os.chdir(self.get_build_dir())


    def run_test(self, plusargs:List[str] = None) -> None:
        plusargs = plusargs or []

        test_name = self.request.node.name

        # call vsim
        cmd = [
            "vsim", "-quiet",
            "-msgmode", "both",
            "-do", "set WildcardFilter [lsearch -not -all -inline $WildcardFilter Memory]",
            "-do", "log -r /*;",
            "-do", "run -all; exit;",
            "-c",
            "-l", "%s.log" % test_name,
            "-wlf", "%s.wlf" % test_name,
            "tb",
        ]
        for plusarg in plusargs:
            cmd.append("+" + plusarg)
        subprocess.run(cmd, check=True)

        self.assertSimLogPass("%s.log" % test_name)


    def tearDown(self) -> None:
        # cd back
        os.chdir(self.original_cwd)


    def assertSimLogPass(self, path: str):
        self.assertTrue(os.path.isfile(path))

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("# ** Error"):
                    self.fail(line)
                elif line.startswith("# ** Fatal"):
                    self.fail(line)
