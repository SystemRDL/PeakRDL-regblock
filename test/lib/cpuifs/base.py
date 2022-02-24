from typing import List, TYPE_CHECKING
import os
import inspect

import jinja2 as jj

from peakrdl.regblock.cpuif.base import CpuifBase

from ..sv_line_anchor import SVLineAnchor

if TYPE_CHECKING:
    from peakrdl.regblock import RegblockExporter
    from ..sim_testcase import SimTestCase

class CpuifTestMode:
    cpuif_cls = None # type: CpuifBase

    # Files required by the DUT
    rtl_files = []  # type: List[str]

    # Files required by the sim testbench
    tb_files = [] # type: List[str]

    tb_template = ""

    def _translate_paths(self, files: List[str]) -> List[str]:
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        cwd = os.getcwd()

        new_files = []
        for file in files:
            relpath = os.path.relpath(
                os.path.join(class_dir, file),
                cwd
            )
            if relpath not in new_files:
                new_files.append(relpath)
        return new_files

    def get_sim_files(self) -> List[str]:
        return self._translate_paths(self.rtl_files + self.tb_files)

    def get_synth_files(self) -> List[str]:
        return self._translate_paths(self.rtl_files)

    def get_tb_inst(self, tb_cls: 'SimTestCase', exporter: 'RegblockExporter') -> str:
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        loader = jj.FileSystemLoader(class_dir)
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
            extensions=[SVLineAnchor],
        )

        context = {
            "cpuif": self,
            "cls": tb_cls,
            "exporter": exporter,
            "type": type,
        }

        template = jj_env.get_template(self.tb_template)

        return template.render(context)
