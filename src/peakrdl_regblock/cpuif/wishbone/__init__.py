from ..base import CpuifBase
from ...utils import clog2

class Wishbone_Cpuif(CpuifBase):
    template_path = "wishbone_tmpl.sv"
    is_interface = True

    @property
    def port_declaration(self) -> str:
        return "wishbone_intf.agent wb"

    def signal(self, name:str) -> str:
        return "wb." + name

class Wishbone_Cpuif_flattened(Wishbone_Cpuif):
    is_interface = False

    @property
    def port_declaration(self) -> str:
        lines = [
            "input wire " + self.signal("cyc"),
            "input wire " + self.signal("stb"),
            "input wire " + self.signal("we"),
            "output logic " + self.signal("stall"),
            f"input wire [{self.addr_width-1}:0] " + self.signal("adr"),
            f"input wire [{self.data_width-1}:0] " + self.signal("odat"),
            f"input wire [{self.data_width_bytes-1}:0] " + self.signal("sel"),
            "output logic " + self.signal("ack"),
            "output logic " + self.signal("err"),
            f"output logic [{self.data_width-1}:0] " + self.signal("idat")
        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "wb_" + name
