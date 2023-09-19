{% sv_line_anchor %}
logic s_cpuif_req;
logic s_cpuif_req_is_wr;
logic [{{exporter.cpuif.addr_width-1}}:0] s_cpuif_addr;
logic [{{exporter.cpuif.data_width-1}}:0] s_cpuif_wr_data;
logic [{{exporter.cpuif.data_width-1}}:0] s_cpuif_wr_biten;
logic s_cpuif_req_stall_wr;
logic s_cpuif_req_stall_rd;
logic s_cpuif_rd_ack;
logic s_cpuif_rd_err;
logic [{{exporter.cpuif.data_width-1}}:0] s_cpuif_rd_data;
logic s_cpuif_wr_ack;
logic s_cpuif_wr_err;
passthrough_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .m_cpuif_req(s_cpuif_req),
    .m_cpuif_req_is_wr(s_cpuif_req_is_wr),
    .m_cpuif_addr(s_cpuif_addr),
    .m_cpuif_wr_data(s_cpuif_wr_data),
    .m_cpuif_wr_biten(s_cpuif_wr_biten),
    .m_cpuif_req_stall_wr(s_cpuif_req_stall_wr),
    .m_cpuif_req_stall_rd(s_cpuif_req_stall_rd),
    .m_cpuif_rd_ack(s_cpuif_rd_ack),
    .m_cpuif_rd_err(s_cpuif_rd_err),
    .m_cpuif_rd_data(s_cpuif_rd_data),
    .m_cpuif_wr_ack(s_cpuif_wr_ack),
    .m_cpuif_wr_err(s_cpuif_wr_err)
);
