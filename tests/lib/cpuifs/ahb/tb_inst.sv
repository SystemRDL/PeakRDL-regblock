{% sv_line_anchor %}
ahb_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) s_ahb();
ahb_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .m_ahb(s_ahb)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}
wire s_ahb_hsel;
wire s_ahb_hwrite;
wire [1:0] s_ahb_htrans;
wire [2:0] s_ahb_hsize;
wire [{{exporter.cpuif.addr_width - 1}}:0] s_ahb_haddr;
wire [{{exporter.cpuif.data_width - 1}}:0] s_ahb_hwdata;
wire s_ahb_hready;
wire [{{exporter.cpuif.data_width - 1}}:0] s_ahb_hrdata;
wire s_ahb_hresp;
assign s_ahb_hsel = s_ahb.HSEL;
assign s_ahb_hwrite = s_ahb.HWRITE;
assign s_ahb_htrans = s_ahb.HTRANS;
assign s_ahb_hsize = s_ahb.HSIZE;
assign s_ahb_haddr = s_ahb.HADDR;
assign s_ahb_hwdata = s_ahb.HWDATA;
assign s_ahb.HREADY = s_ahb_hready;
assign s_ahb.HRDATA = s_ahb_hrdata;
assign s_ahb.HRESP = s_ahb_hresp;
{% endif %}

