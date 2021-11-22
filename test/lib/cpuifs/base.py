from typing import List, TYPE_CHECKING
import os
import inspect

import jinja2 as jj

from peakrdl.regblock.cpuif.base import CpuifBase

if TYPE_CHECKING:
    from peakrdl.regblock import RegblockExporter
    from ..regblock_testcase import RegblockTestCase

class CpuifTestMode:
    cpuif_cls = None # type: CpuifBase
    tb_files = [] # type: List[str]
    tb_template = ""

    def get_tb_files(self) -> List[str]:
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        cwd = os.getcwd()

        tb_files = []
        for file in self.tb_files:
            relpath = os.path.relpath(
                os.path.join(class_dir, file),
                cwd
            )
            tb_files.append(relpath)
        return tb_files


    def get_tb_inst(self, tb_cls: 'RegblockTestCase', exporter: 'RegblockExporter') -> str:
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        loader = jj.FileSystemLoader(
            os.path.join(class_dir)
        )
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
        )

        context = {
            "cpuif": self,
            "cls": tb_cls,
            "exporter": exporter,
            "type": type,
        }

        template = jj_env.get_template(self.tb_template)
        return template.render(context)
