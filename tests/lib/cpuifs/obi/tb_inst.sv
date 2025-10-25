{% sv_line_anchor %}
obi_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) obi();
obi_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .m_obi(obi)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}

wire obi_req;
wire obi_gnt;
wire [{{exporter.cpuif.addr_width - 1}}:0] obi_addr;
wire obi_we;
wire [{{exporter.cpuif.data_width_bytes - 1}}:0] obi_be;
wire [{{exporter.cpuif.data_width - 1}}:0] obi_wdata;
wire [0:0] obi_aid;
wire obi_rvalid;
wire obi_rready;
wire [{{exporter.cpuif.data_width - 1}}:0] obi_rdata;
wire obi_err;
wire [0:0] obi_rid;
assign obi_req = obi.req;
assign obi.gnt = obi_gnt;
assign obi_addr = obi.addr;
assign obi_we = obi.we;
assign obi_be = obi.be;
assign obi_wdata = obi.wdata;
assign obi_aid = obi.aid;
assign obi.rvalid = obi_rvalid;
assign obi_rready = obi.rready;
assign obi.rdata = obi_rdata;
assign obi.err = obi_err;
assign obi.rid = obi_rid;
{% endif %}
