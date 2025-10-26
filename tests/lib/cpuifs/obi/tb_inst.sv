{% sv_line_anchor %}
obi_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) s_obi();
obi_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .m_obi(s_obi)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}

wire s_obi_req;
wire s_obi_gnt;
wire [{{exporter.cpuif.addr_width - 1}}:0] s_obi_addr;
wire s_obi_we;
wire [{{exporter.cpuif.data_width_bytes - 1}}:0] s_obi_be;
wire [{{exporter.cpuif.data_width - 1}}:0] s_obi_wdata;
wire [0:0] s_obi_aid;
wire s_obi_rvalid;
wire s_obi_rready;
wire [{{exporter.cpuif.data_width - 1}}:0] s_obi_rdata;
wire s_obi_err;
wire [0:0] s_obi_rid;
assign s_obi_req = s_obi.req;
assign s_obi.gnt = s_obi_gnt;
assign s_obi_addr = s_obi.addr;
assign s_obi_we = s_obi.we;
assign s_obi_be = s_obi.be;
assign s_obi_wdata = s_obi.wdata;
assign s_obi_aid = s_obi.aid;
assign s_obi.rvalid = s_obi_rvalid;
assign s_obi_rready = s_obi.rready;
assign s_obi.rdata = s_obi_rdata;
assign s_obi.err = s_obi_err;
assign s_obi.rid = s_obi_rid;
{% endif %}
