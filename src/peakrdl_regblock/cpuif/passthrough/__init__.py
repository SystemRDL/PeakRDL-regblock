from typing import Union

from ..base import CpuifBase

class PassthroughCpuif(CpuifBase):
    template_path = "passthrough_tmpl.vhd"

    @property
    def signal_declaration(self) -> str:
        return ""

    @property
    def package_name(self) -> Union[str, None]:
        return None

    @property
    def port_declaration(self) -> str:
        lines = [
            "s_cpuif_req : in std_logic;",
            "s_cpuif_req_is_wr : in std_logic;",
           f"s_cpuif_addr : in std_logic_vector({self.addr_width-1} downto 0);",
           f"s_cpuif_wr_data : in std_logic_vector({self.data_width-1} downto 0);",
           f"s_cpuif_wr_biten : in std_logic_vector({self.data_width-1} downto 0);",
            "s_cpuif_req_stall_wr : out std_logic;",
            "s_cpuif_req_stall_rd : out std_logic;",
            "s_cpuif_rd_ack : out std_logic;",
            "s_cpuif_rd_err : out std_logic;",
           f"s_cpuif_rd_data : out std_logic_vector({self.data_width-1} downto 0);",
            "s_cpuif_wr_ack : out std_logic;",
            "s_cpuif_wr_err : out std_logic",
        ]
        return "\n".join(lines)
