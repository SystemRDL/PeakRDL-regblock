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
logic avalon_read;
logic avalon_write;
logic avalon_waitrequest;
logic [{{exporter.cpuif.word_addr_width - 1}}:0] avalon_address;
logic [{{exporter.cpuif.data_width - 1}}:0] avalon_writedata;
logic [{{exporter.cpuif.data_width_bytes - 1}}:0] avalon_byteenable;
logic avalon_readdatavalid;
logic avalon_writeresponsevalid;
logic [{{exporter.cpuif.data_width - 1}}:0] avalon_readdata;
logic [1:0] avalon_response;
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
