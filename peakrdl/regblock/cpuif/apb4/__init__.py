from ..base import CpuifBase

class APB4_Cpuif(CpuifBase):
    template_path = "cpuif/apb4/apb4_tmpl.sv"

    @property
    def port_declaration(self) -> str:
        return "apb4_intf.slave s_apb"

    def signal(self, name:str) -> str:
        return "s_apb." + name


class APB4_Cpuif_flattened(APB4_Cpuif):
    @property
    def port_declaration(self) -> str:
        # TODO: Reference data/addr width from verilog parameter perhaps?
        lines = [
            "input wire " + self.signal("psel"),
            "input wire " + self.signal("penable"),
            "input wire " + self.signal("pwrite"),
            "input wire " + self.signal("pprot"),
            f"input wire [{self.addr_width-1}:0] " + self.signal("paddr"),
            f"input wire [{self.data_width-1}:0] " + self.signal("pwdata"),
            f"input wire [{(self.data_width / 8)-1}:0] " + self.signal("pstrb"),
            "output logic " + self.signal("pready"),
            f"output logic [{self.data_width-1}:0] " + self.signal("prdata"),
            "output logic " + self.signal("pslverr"),
        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_apb_" + name
