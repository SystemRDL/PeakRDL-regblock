from typing import TYPE_CHECKING, Optional
import inspect
import os

import jinja2 as jj

from ..utils import get_always_ff_event, clog2, is_pow2

if TYPE_CHECKING:
    from ..exporter import RegblockExporter
    from systemrdl import SignalNode

class CpuifBase:

    # Path is relative to the location of the class that assigns this variable
    template_path = ""

    def __init__(self, exp:'RegblockExporter', cpuif_reset:Optional['SignalNode'], data_width:int=32, addr_width:int=32):
        self.exp = exp
        self.reset = cpuif_reset
        self.data_width = data_width
        self.addr_width = addr_width

    @property
    def port_declaration(self) -> str:
        raise NotImplementedError()


    def _get_template_path_class_dir(self) -> str:
        """
        Traverse up the MRO and find the first class that explicitly assigns
        template_path. Returns the directory that contains the class definition.
        """
        for cls in inspect.getmro(self.__class__):
            if "template_path" in cls.__dict__:
                class_dir = os.path.dirname(inspect.getfile(cls))
                return class_dir
        raise RuntimeError


    def get_implementation(self) -> str:
        class_dir = self._get_template_path_class_dir()
        loader = jj.FileSystemLoader(class_dir)
        jj_env = jj.Environment(
            loader=loader,
            undefined=jj.StrictUndefined,
        )

        context = {
            "cpuif": self,
            "get_always_ff_event": lambda resetsignal : get_always_ff_event(self.exp.dereferencer, resetsignal),
            "get_resetsignal": self.exp.dereferencer.get_resetsignal,
            "clog2": clog2,
            "is_pow2": is_pow2,
        }

        template = jj_env.get_template(self.template_path)
        return template.render(context)
