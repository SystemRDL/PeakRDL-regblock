from ..base import CpuifBase

class AXI4Lite_Cpuif(CpuifBase):
    template_path = "axi4lite_tmpl.sv"

    @property
    def port_declaration(self) -> str:
        return "axi4lite_intf.slave s_axil"

    def signal(self, name:str) -> str:
        return "s_axil." + name.upper()

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
            "output logic " + self.signal("awready"),
            "input logic " + self.signal("awvalid"),
            f"input logic [{self.addr_width-1}:0] " + self.signal("awaddr"),
            "input logic [2:0] " + self.signal("awprot"),

            "output logic " + self.signal("wready"),
            "input logic " + self.signal("wvalid"),
            f"input logic [{self.data_width-1}:0] " + self.signal("wdata"),
            f"input logic [{self.data_width_bytes-1}:0]" + self.signal("wstrb"),

            "input logic " + self.signal("bready"),
            "output logic " + self.signal("bvalid"),
            "output logic [1:0] " + self.signal("bresp"),

            "output logic " + self.signal("arready"),
            "input logic " + self.signal("arvalid"),
            f"input logic [{self.addr_width-1}:0] " + self.signal("araddr"),
            "input logic [2:0] " + self.signal("arprot"),

            "input logic " + self.signal("rready"),
            "output logic " + self.signal("rvalid"),
            f"output logic [{self.data_width-1}:0] " + self.signal("rdata"),
            "output logic [1:0] " + self.signal("rresp"),
        ]
        return ",\n".join(lines)

    def signal(self, name:str) -> str:
        return "s_axil_" + name
