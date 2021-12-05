{% sv_line_anchor %}
apb3_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) s_apb();
apb3_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif(
    .clk(clk),
    .rst(rst),
    .m_apb(s_apb)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}
wire s_apb_psel;
wire s_apb_penable;
wire s_apb_pwrite;
wire [{{exporter.cpuif.addr_width - 1}}:0] s_apb_paddr;
wire [{{exporter.cpuif.data_width - 1}}:0] s_apb_pwdata;
wire s_apb_pready;
wire [{{exporter.cpuif.data_width - 1}}:0] s_apb_prdata;
wire s_apb_pslverr;
assign s_apb_psel = s_apb.PSEL;
assign s_apb_penable = s_apb.PENABLE;
assign s_apb_pwrite = s_apb.PWRITE;
assign s_apb_paddr = s_apb.PADDR;
assign s_apb_pwdata = s_apb.PWDATA;
assign s_apb.PREADY = s_apb_pready;
assign s_apb.PRDATA = s_apb_prdata;
assign s_apb.PSLVERR = s_apb_pslverr;
{% endif %}
