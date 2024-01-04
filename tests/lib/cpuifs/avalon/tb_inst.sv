{% sv_line_anchor %}
avalon_mm_intf #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.word_addr_width}})
) avalon();
avalon_mm_intf_driver #(
    .DATA_WIDTH({{exporter.cpuif.data_width}}),
    .ADDR_WIDTH({{exporter.cpuif.addr_width}})
) cpuif (
    .clk(clk),
    .rst(rst),
    .avalon(avalon)
);
{% if type(cpuif).__name__.startswith("Flat") %}
{% sv_line_anchor %}
wire avalon_read;
wire avalon_write;
wire avalon_waitrequest;
wire [{{exporter.cpuif.word_addr_width - 1}}:0] avalon_address;
wire [{{exporter.cpuif.data_width - 1}}:0] avalon_writedata;
wire [{{exporter.cpuif.data_width_bytes - 1}}:0] avalon_byteenable;
wire avalon_readdatavalid;
wire avalon_writeresponsevalid;
wire [{{exporter.cpuif.data_width - 1}}:0] avalon_readdata;
wire [1:0] avalon_response;
assign avalon_read = avalon.read;
assign avalon_write = avalon.write;
assign avalon.waitrequest = avalon_waitrequest;
assign avalon_address = avalon.address;
assign avalon_writedata = avalon.writedata;
assign avalon_byteenable = avalon.byteenable;
assign avalon.readdatavalid = avalon_readdatavalid;
assign avalon.writeresponsevalid = avalon_writeresponsevalid;
assign avalon.readdata = avalon_readdata;
assign avalon.response = avalon_response;
{% endif %}
