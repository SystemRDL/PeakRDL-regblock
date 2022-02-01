{% sv_line_anchor %}
axi4lite_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) s_axil();
axi4lite_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .m_axil(s_axil)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}
wire s_axil_awready;
wire s_axil_awvalid;
wire [{{exporter.cpuif.addr_width - 1}}:0] s_axil_awaddr;
wire [2:0] s_axil_awprot;
wire s_axil_wready;
wire s_axil_wvalid;
wire [{{exporter.cpuif.data_width - 1}}:0] s_axil_wdata;
wire [{{exporter.cpuif.data_width_bytes - 1}}:0] s_axil_wstrb;
wire s_axil_bready;
wire s_axil_bvalid;
wire [1:0] s_axil_bresp;
wire s_axil_arready;
wire s_axil_arvalid;
wire [{{exporter.cpuif.addr_width - 1}}:0] s_axil_araddr;
wire [2:0] s_axil_arprot;
wire s_axil_rready;
wire s_axil_rvalid;
wire [{{exporter.cpuif.data_width - 1}}:0] s_axil_rdata;
wire [1:0] s_axil_rresp;
assign s_axil.AWREADY = s_axil_awready;
assign s_axil_awvalid = s_axil.AWVALID;
assign s_axil_awaddr = s_axil.AWADDR;
assign s_axil_awprot = s_axil.AWPROT;
assign s_axil.WREADY = s_axil_wready;
assign s_axil_wvalid = s_axil.WVALID;
assign s_axil_wdata = s_axil.WDATA;
assign s_axil_wstrb = s_axil.WSTRB;
assign s_axil_bready = s_axil.BREADY;
assign s_axil.BVALID = s_axil_bvalid;
assign s_axil.BRESP = s_axil_bresp;
assign s_axil.ARREADY = s_axil_arready;
assign s_axil_arvalid = s_axil.ARVALID;
assign s_axil_araddr = s_axil.ARADDR;
assign s_axil_arprot = s_axil.ARPROT;
assign s_axil_rready = s_axil.RREADY;
assign s_axil.RVALID = s_axil_rvalid;
assign s_axil.RDATA = s_axil_rdata;
assign s_axil.RRESP = s_axil_rresp;
{% endif %}
