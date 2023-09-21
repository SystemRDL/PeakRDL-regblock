from ..base import CpuifBase

class APB3_Cpuif(CpuifBase):
    template_path = "apb3_tmpl.sv"

    @property
    def port_declaration(self) -> str:
        return "apb3_intf.slave s_apb"

    def signal(self, name:str) -> str:
        return "s_apb." + name.upper()


class APB3_Cpuif_flattened(APB3_Cpuif):
    @property
    def port_declaration(self) -> str:
        lines = [
            "input logic " + self.signal("psel"),
            "input logic " + self.signal("penable"),
            "input logic " + self.signal("pwrite"),
            f"input logic [{self.addr_width-1}:0] " + self.signal("paddr"),
            f"input logic [{self.data_width-1}:0] " + self.signal("pwdata"),
            "output logic " + self.signal("pready"),
            f"output logic [{self.data_width-1}:0] " + self.signal("prdata"),
            "output logic " + self.signal("pslverr"),
        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_apb_" + name
