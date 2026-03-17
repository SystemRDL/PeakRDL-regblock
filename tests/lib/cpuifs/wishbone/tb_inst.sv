{% sv_line_anchor %}
wishbone_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) wb();
wishbone_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .wb(wb)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}
wire wb_cyc;
wire wb_stb;
wire wb_we;
wire wb_stall;
wire [{{exporter.cpuif.addr_width - 1}}:0] wb_adr;
wire [{{exporter.cpuif.data_width - 1}}:0] wb_odat;
wire [{{exporter.cpuif.data_width_bytes - 1}}:0] wb_sel;
wire wb_ack;
wire wb_err;
wire [{{exporter.cpuif.data_width - 1}}:0] wb_idat;
assign wb_cyc = wb.cyc;
assign wb_stb = wb.stb;
assign wb_we = wb.we;
assign wb.stall = wb_stall;
assign wb_adr = wb.adr;
assign wb_odat = wb.odat;
assign wb_sel = wb.sel;
assign wb.ack = wb_ack;
assign wb.err = wb_err;
assign wb.idat = wb_idat;
{% endif %}
