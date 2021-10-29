from typing import TYPE_CHECKING

from ..utils import get_always_ff_event

if TYPE_CHECKING:
    from ..exporter import RegblockExporter
    from ..signals import SignalBase

class CpuifBase:
    template_path = "cpuif/base_tmpl.sv"

    def __init__(self, exp:'RegblockExporter', cpuif_reset:'SignalBase', data_width:int=32, addr_width:int=32):
        self.exp = exp
        self.cpuif_reset = cpuif_reset
        self.data_width = data_width
        self.addr_width = addr_width

    @property
    def port_declaration(self) -> str:
        raise NotImplementedError()

    def get_implementation(self) -> str:
        context = {
            "cpuif": self,
            "cpuif_reset": self.cpuif_reset,
            "data_width": self.data_width,
            "addr_width": self.addr_width,
            "get_always_ff_event": get_always_ff_event,
        }

        template = self.exp.jj_env.get_template(self.template_path)
        return template.render(context)
