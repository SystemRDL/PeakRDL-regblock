from typing import List

from ..base import CpuifBase

class OBI_Cpuif(CpuifBase):
    template_path = "obi_tmpl.sv"
    is_interface = True

    @property
    def port_declaration(self) -> str:
        return "obi_intf.subordinate s_obi"

    def signal(self, name: str) -> str:
        return "s_obi." + name

    @property
    def regblock_latency(self) -> int:
        return max(self.exp.ds.min_read_latency, self.exp.ds.min_write_latency)

    @property
    def max_outstanding(self) -> int:
        """
        OBI supports multiple outstanding transactions.
        Best performance when max outstanding is design latency + 1.
        """
        return self.regblock_latency + 1


class OBI_Cpuif_flattened(OBI_Cpuif):
    is_interface = False

    @property
    def port_declaration(self) -> str:
        lines = [
            # OBI Request Channel (A)
            "input wire " + self.signal("req"),
            "output logic " + self.signal("gnt"),
            f"input wire [{self.addr_width-1}:0] " + self.signal("addr"),
            "input wire " + self.signal("we"),
            f"input wire [{self.data_width//8-1}:0] " + self.signal("be"),
            f"input wire [{self.data_width-1}:0] " + self.signal("wdata"),
            "input wire [ID_WIDTH-1:0] " + self.signal("aid"),

            # OBI Response Channel (R)
            "output logic " + self.signal("rvalid"),
            "input wire " + self.signal("rready"),
            f"output logic [{self.data_width-1}:0] " + self.signal("rdata"),
            "output logic " + self.signal("err"),
            "output logic [ID_WIDTH-1:0] " + self.signal("rid"),
        ]
        return ",\n".join(lines)

    def signal(self, name: str) -> str:
        return "s_obi_" + name

    @property
    def parameters(self) -> List[str]:
        return ["parameter ID_WIDTH = 1"]
