from ..base import CpuifBase

class APB4_Cpuif(CpuifBase):
    template_path = "apb4_tmpl.sv"

    @property
    def port_declaration(self) -> str:
        return "apb4_intf.slave s_apb"

    def signal(self, name:str) -> str:
        return "s_apb." + name.upper()


class APB4_Cpuif_flattened(APB4_Cpuif):
    @property
    def port_declaration(self) -> str:
        lines = [
            "input logic " + self.signal("psel"),
            "input logic " + self.signal("penable"),
            "input logic " + self.signal("pwrite"),
            "input logic [2:0] " + self.signal("pprot"),
            f"input logic [{self.addr_width-1}:0] " + self.signal("paddr"),
            f"input logic [{self.data_width-1}:0] " + self.signal("pwdata"),
            f"input logic [{self.data_width_bytes-1}:0] " + self.signal("pstrb"),
            "output logic " + self.signal("pready"),
            f"output logic [{self.data_width-1}:0] " + self.signal("prdata"),
            "output logic " + self.signal("pslverr"),
        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_apb_" + name
