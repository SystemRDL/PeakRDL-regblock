{% extends "cpuif/base_tmpl.sv" %}
{%- import "utils_tmpl.sv" as utils with context %}

{% block body %}
// Request
logic is_active;
{%- call utils.AlwaysFF(cpuif_reset) %}
    if({{cpuif_reset.activehigh_identifier}}) begin
        is_active <= '0;
        cpuif_req <= '0;
        cpuif_req_is_wr <= '0;
        cpuif_addr <= '0;
        cpuif_wr_data <= '0;
        cpuif_wr_bitstrb <= '0;
    end else begin
        if(~is_active) begin
            if({{cpuif.signal("psel")}}) begin
                is_active <= '1;
                cpuif_req <= '1;
                cpuif_req_is_wr <= {{cpuif.signal("pwrite")}};
                cpuif_addr <= {{cpuif.signal("paddr")}}[ADDR_WIDTH-1:0];
                cpuif_wr_data <= {{cpuif.signal("pwdata")}};
                for(int i=0; i<DATA_WIDTH/8; i++) begin
                    cpuif_wr_bitstrb[i*8 +: 8] <= {{"{8{"}}{{cpuif.signal("pstrb")}}[i]{{"}}"}};
                end
            end
        end else begin
            cpuif_req <= '0;
            if(cpuif_rd_ack || cpuif_wr_ack) begin
                is_active <= '0;
            end
        end
    end
{%- endcall %}

// Response
assign {{cpuif.signal("pready")}} = cpuif_rd_ack | cpuif_wr_ack;
assign {{cpuif.signal("prdata")}} = cpuif_rd_data;
assign {{cpuif.signal("pslverr")}} = cpuif_rd_err | cpuif_wr_err;
{%- endblock body%}
