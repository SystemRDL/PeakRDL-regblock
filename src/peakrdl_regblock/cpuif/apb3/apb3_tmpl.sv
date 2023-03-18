// Request
logic is_active;
always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        is_active <= '0;
        cpuif_req <= '0;
        cpuif_req_is_wr <= '0;
        cpuif_addr <= '0;
        cpuif_wr_data <= '0;
    end else begin
        if(~is_active) begin
            if({{cpuif.signal("psel")}}) begin
                is_active <= '1;
                cpuif_req <= '1;
                cpuif_req_is_wr <= {{cpuif.signal("pwrite")}};
                {%- if cpuif.data_width == 8 %}
                cpuif_addr <= {{cpuif.signal("paddr")}}[{{cpuif.addr_width-1}}:0];
                {%- else %}
                cpuif_addr <= { {{-cpuif.signal("paddr")}}[{{cpuif.addr_width-1}}:{{clog2(cpuif.data_width_bytes)}}], {{clog2(cpuif.data_width_bytes)}}'b0};
                {%- endif %}
                cpuif_wr_data <= {{cpuif.signal("pwdata")}};
            end
        end else begin
            cpuif_req <= '0;
            if(cpuif_rd_ack || cpuif_wr_ack) begin
                is_active <= '0;
            end
        end
    end
end
assign cpuif_wr_biten = '1;

// Response
assign {{cpuif.signal("pready")}} = cpuif_rd_ack | cpuif_wr_ack;
assign {{cpuif.signal("prdata")}} = cpuif_rd_data;
assign {{cpuif.signal("pslverr")}} = cpuif_rd_err | cpuif_wr_err;
