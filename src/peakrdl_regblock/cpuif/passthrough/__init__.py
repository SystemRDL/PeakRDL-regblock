from ..base import CpuifBase

class PassthroughCpuif(CpuifBase):
    template_path = "passthrough_tmpl.sv"

    @property
    def port_declaration(self) -> str:
        lines = [
            "input logic s_cpuif_req",
            "input logic s_cpuif_req_is_wr",
            f"input logic [{self.addr_width-1}:0] s_cpuif_addr",
            f"input logic [{self.data_width-1}:0] s_cpuif_wr_data",
            f"input logic [{self.data_width-1}:0] s_cpuif_wr_biten",
            "output logic s_cpuif_req_stall_wr",
            "output logic s_cpuif_req_stall_rd",
            "output logic s_cpuif_rd_ack",
            "output logic s_cpuif_rd_err",
            f"output logic [{self.data_width-1}:0] s_cpuif_rd_data",
            "output logic s_cpuif_wr_ack",
            "output logic s_cpuif_wr_err",
        ]
        return ",\n".join(lines)
