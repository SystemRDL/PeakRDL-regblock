from typing import Union

from ..base import CpuifBase

class APB3_Cpuif(CpuifBase):
    template_path = "apb3_tmpl.vhd"

    @property
    def package_name(self) -> Union[str, None]:
        return "apb3_intf_pkg"

    @property
    def port_declaration(self) -> str:
        return "\n".join([
            "s_apb_i : in apb3_slave_in_intf(",
           f"    PADDR({self.addr_width-1} downto 0),",
           f"    PWDATA({self.data_width-1} downto 0)",
            ");",
            "s_apb_o : out apb3_slave_out_intf(",
           f"    PRDATA({self.data_width-1} downto 0)",
            ")",
        ])

    @property
    def signal_declaration(self) -> str:
        return "signal apb_is_active : std_logic;"

    def signal(self, name:str) -> str:
        if name.upper().endswith(("RDATA", "READY", "SLVERR")):
            return "s_apb_o." + name.upper()
        else:
            return "s_apb_i." + name.upper()


class APB3_Cpuif_flattened(APB3_Cpuif):
    @property
    def package_name(self) -> Union[str, None]:
        return None

    @property
    def port_declaration(self) -> str:
        lines = [
            self.signal("psel")    +  " : in std_logic;",
            self.signal("penable") +  " : in std_logic;",
            self.signal("pwrite")  +  " : in std_logic;",
            self.signal("paddr")   + f" : in std_logic_vector({self.addr_width-1} downto 0);",
            self.signal("pwdata")  + f" : in std_logic_vector({self.data_width-1} downto 0);",
            self.signal("pready")  +  " : out std_logic;",
            self.signal("prdata")  + f" : out std_logic_vector({self.data_width-1} downto 0);",
            self.signal("pslverr") +  " : out std_logic",
        ]
        return "\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_apb_" + name
