// Request
always_comb begin
    cpuif_req = {{cpuif.signal("read")}} | {{cpuif.signal("write")}};
    cpuif_req_is_wr = {{cpuif.signal("write")}};
    {%- if cpuif.data_width_bytes == 1 %}
    cpuif_addr = {{cpuif.signal("address")}};
    {%- else %}
    cpuif_addr = { {{-cpuif.signal("address")}}, {{clog2(cpuif.data_width_bytes)}}'b0};
    {%- endif %}
    cpuif_wr_data = {{cpuif.signal("writedata")}};
    for(int i=0; i<{{cpuif.data_width_bytes}}; i++) begin
        cpuif_wr_biten[i*8 +: 8] <= {8{ {{-cpuif.signal("byteenable")}}[i]}};
    end
    {{cpuif.signal("waitrequest")}} = (cpuif_req_stall_rd & {{cpuif.signal("read")}}) | (cpuif_req_stall_wr & {{cpuif.signal("write")}});
end

// Response
always_comb begin
    {{cpuif.signal("readdatavalid")}} = cpuif_rd_ack;
    {{cpuif.signal("writeresponsevalid")}} = cpuif_wr_ack;
    {{cpuif.signal("readdata")}} = cpuif_rd_data;
    if(cpuif_rd_err || cpuif_wr_err) begin
        // SLVERR
        {{cpuif.signal("response")}} = 2'b10;
    end else begin
        // OK
        {{cpuif.signal("response")}} = 2'b00;
    end
end
