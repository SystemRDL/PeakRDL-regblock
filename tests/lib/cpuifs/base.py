from typing import List, TYPE_CHECKING
import os
import inspect

import jinja2 as jj

from peakrdl_regblock.cpuif.base import CpuifBase as SvCpuifBase
from peakrdl_regblock_vhdl.cpuif.base import CpuifBase as VhdlCpuifBase

from ..sv_line_anchor import SVLineAnchor

if TYPE_CHECKING:
    from peakrdl_regblock_vhdl import RegblockExporter
    from ..sim_testcase import SimTestCase

class CpuifTestMode:
    sv_cpuif_cls = None # type: SvCpuifBase
    vhdl_cpuif_cls = None # type: VhdlCpuifBase

    # Files required by the DUT
    # Paths are relative to the class that assigns this
    rtl_files = []  # type: List[str]

    # Files required by the sim testbench
    # Paths are relative to the class that assigns this
    tb_files = [] # type: List[str]

    # Path is relative to the class that assigns this
    tb_template = ""

    @staticmethod
    def input_signals(cpuif: SvCpuifBase) -> list[tuple[str, int]]:
        raise NotImplementedError()

    @staticmethod
    def output_signals(cpuif: SvCpuifBase) -> list[tuple[str, int]]:
        raise NotImplementedError()

    @classmethod
    def signals(cls, cpuif: SvCpuifBase) -> list[tuple[str, int]]:
        results = cls.input_signals(cpuif)
        results.extend(cls.output_signals(cpuif))
        return results

    def _get_class_dir_of_variable(self, varname:str) -> str:
        """
        Traverse up the MRO and find the first class that explicitly assigns
        the variable of name varname. Returns the directory that contains the
        class definition.
        """
        for cls in inspect.getmro(self.__class__):
            if varname in cls.__dict__:
                class_dir = os.path.dirname(inspect.getfile(cls))
                return class_dir
        raise RuntimeError


    def _get_file_paths(self, varname:str) -> List[str]:
        class_dir = self._get_class_dir_of_variable(varname)
        files = getattr(self, varname)
        cwd = os.getcwd()

        new_files = []
        for file in files:
            relpath = os.path.relpath(
                os.path.join(class_dir, file),
                cwd
            )
            new_files.append(relpath)
        return new_files


    def get_sim_files(self) -> List[str]:
        files = self._get_file_paths("rtl_files") + self._get_file_paths("tb_files")
        unique_files = []
        [unique_files.append(f) for f in files if f not in unique_files]
        return unique_files


    def get_synth_files(self) -> List[str]:
        return self._get_file_paths("rtl_files")


    def get_tb_inst(self, testcase: 'SimTestCase', exporter: 'RegblockExporter') -> str:
        class_dir = self._get_class_dir_of_variable("tb_template")
        loader = jj.FileSystemLoader(class_dir)
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
            extensions=[SVLineAnchor],
        )

        context = {
            "cpuif": self,
            "testcase": testcase,
            "exporter": exporter,
            "type": type,
        }

        template = jj_env.get_template(self.tb_template)

        return template.render(context)
