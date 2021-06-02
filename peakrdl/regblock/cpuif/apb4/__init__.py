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
            "input wire %s" % self.signal("psel"),
            "input wire %s" % self.signal("penable"),
            "input wire %s" % self.signal("pwrite"),
            "input wire %s" % self.signal("pprot"),
            "input wire [%d-1:0] %s" % (self.addr_width, self.signal("paddr")),
            "input wire [%d-1:0] %s" % (self.data_width, self.signal("pwdata")),
            "input wire [%d-1:0] %s" % (self.data_width / 8, self.signal("pstrb")),
            "output logic %s" % self.signal("pready"),
            "output logic [%d-1:0] %s" % (self.data_width, self.signal("prdata")),
            "output logic %s" % self.signal("pslverr"),
        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_apb_" + name
