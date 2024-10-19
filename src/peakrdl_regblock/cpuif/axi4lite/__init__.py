from ..base import CpuifBase

class AXI4Lite_Cpuif(CpuifBase):
    template_path = "axi4lite_tmpl.vhd"

    @property
    def port_declaration(self) -> str:
        return "\n".join([
            "s_axil_i : in axi4lite_slave_in_intf(",
           f"    AWADDR({self.addr_width-1} downto 0),",
           f"    WDATA({self.data_width-1} downto 0),",
           f"    WSTRB({self.data_width_bytes-1} downto 0),",
           f"    ARADDR({self.addr_width-1} downto 0)",
            ");",
            "s_axil_o : out axi4lite_slave_out_intf(",
           f"    RDATA({self.data_width-1} downto 0)",
            ");",
        ])

    def signal(self, name:str) -> str:
        name = name.upper()
        if name.startswith(("B", "R")):
            if name.endswith("READY"):
                return "s_axil_i." + name
            else:
                return "s_axil_o." + name
        else:
            if name.endswith("READY"):
                return "s_axil_o." + name
            else:
                return "s_axil_i." + name

    @property
    def regblock_latency(self) -> int:
        return max(self.exp.ds.min_read_latency, self.exp.ds.min_write_latency)

    @property
    def max_outstanding(self) -> int:
        """
        Best pipelined performance is when the max outstanding transactions
        is the design's latency + 2.
        Anything beyond that does not have any effect, aside from adding unnecessary
        logic and additional buffer-bloat latency.
        """
        return self.regblock_latency + 2

    @property
    def resp_buffer_size(self) -> int:
        """
        Response buffer size must be greater or equal to max outstanding
        transactions to prevent response overrun.
        """
        return self.max_outstanding


class AXI4Lite_Cpuif_flattened(AXI4Lite_Cpuif):
    @property
    def port_declaration(self) -> str:
        lines = [
            "s_axil_awready : out std_logic;",
            "s_axil_awvalid : in std_logic;",
           f"s_axil_awaddr : in std_logic_vector({self.addr_width-1} downto 0);",
            "s_axil_awprot : in std_logic_vector(2 downto 0);",

            "s_axil_wready : out std_logic;",
            "s_axil_wvalid : in std_logic;",
           f"s_axil_wdata : in std_logic_vector({self.data_width-1} downto 0);",
           f"s_axil_wstrb : in std_logic_vector({self.data_width_bytes-1} downto 0);",

            "s_axil_bready : in std_logic;",
            "s_axil_bvalid : out std_logic;",
            "s_axil_bresp : out std_logic_vector(1 downto 0);",

            "s_axil_arready : out std_logic;",
            "s_axil_arvalid : in std_logic;",
           f"s_axil_araddr : in std_logic_vector({self.addr_width-1} downto 0);",
            "s_axil_arprot : in std_logic_vector(2 downto 0);",

            "s_axil_rready : in std_logic;",
            "s_axil_rvalid : out std_logic;",
           f"s_axil_rdata : out std_logic_vector({self.data_width-1} downto 0);",
            "s_axil_rresp : out std_logic_vector(1 downto 0);",
        ]
        return "\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_axil_" + name
