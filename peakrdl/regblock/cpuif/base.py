from typing import TYPE_CHECKING, Optional

from ..utils import get_always_ff_event, clog2

if TYPE_CHECKING:
    from ..exporter import RegblockExporter
    from systemrdl import SignalNode

class CpuifBase:
    template_path = ""

    def __init__(self, exp:'RegblockExporter', cpuif_reset:Optional['SignalNode'], data_width:int=32, addr_width:int=32):
        self.exp = exp
        self.reset = cpuif_reset
        self.data_width = data_width
        self.addr_width = addr_width

    @property
    def port_declaration(self) -> str:
        raise NotImplementedError()

    def get_implementation(self) -> str:
        context = {
            "cpuif": self,
            "get_always_ff_event": lambda resetsignal : get_always_ff_event(self.exp.dereferencer, resetsignal),
            "get_resetsignal": self.exp.dereferencer.get_resetsignal,
            "clog2": clog2,
        }

        template = self.exp.jj_env.get_template(self.template_path)
        return template.render(context)
