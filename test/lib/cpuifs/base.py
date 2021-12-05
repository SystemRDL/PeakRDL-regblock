from typing import List, TYPE_CHECKING
import os
import inspect

import jinja2 as jj

from peakrdl.regblock.cpuif.base import CpuifBase

from ..sv_line_anchor import SVLineAnchor

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

        # For consistency, make the template root path relative to the test dir
        template_root_path = os.path.join(os.path.dirname(__file__), "../..")

        loader = jj.FileSystemLoader(
            template_root_path
        )
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

        # template paths are relative to their class.
        # transform to be relative to the root path
        class_dir = os.path.dirname(inspect.getfile(self.__class__))
        template_local_path = os.path.join(class_dir, self.tb_template)
        template_path = os.path.relpath(template_local_path, template_root_path)
        template = jj_env.get_template(template_path)

        return template.render(context)
