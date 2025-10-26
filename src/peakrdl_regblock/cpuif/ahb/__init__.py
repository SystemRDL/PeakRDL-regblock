from ..base import CpuifBase


class AHB_Cpuif(CpuifBase):
    template_path = "ahb_tmpl.sv"
    is_interface = True

    @property
    def port_declaration(self) -> str:
        return "ahb_intf.slave s_ahb"

    def signal(self, name: str) -> str:
        return "s_ahb." + name.upper()


class AHB_Cpuif_flattened(AHB_Cpuif):
    is_interface = False

    @property
    def port_declaration(self) -> str:
        lines = [
            "input wire " + self.signal("hsel"),
            "input wire " + self.signal("hwrite"),
            "input wire [1:0] " + self.signal("htrans"),
            "input wire [2:0] " + self.signal("hsize"),
            f"input wire [{self.addr_width-1}:0] " + self.signal("haddr"),
            f"input wire [{self.data_width-1}:0] " + self.signal("hwdata"),
            "output logic " + self.signal("hready"),
            f"output logic [{self.data_width-1}:0] " + self.signal("hrdata"),
            "output logic " + self.signal("hresp"),
        ]
        return ",\n".join(lines)

    def signal(self, name: str) -> str:
        return "s_ahb_" + name
