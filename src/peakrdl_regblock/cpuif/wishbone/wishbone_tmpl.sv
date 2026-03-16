{%- if cpuif.is_interface -%}
`ifndef SYNTHESIS
    initial begin
        assert_bad_addr_width: assert($bits({{cpuif.signal("adr")}}) >= {{cpuif.addr_width}})
            else $error("Interface address width of %0d is too small. Shall be at least %0d bits", $bits({{cpuif.signal("adr")}}), {{cpuif.addr_width}});
        assert_bad_data_width: assert($bits({{cpuif.signal("odat")}}) == {{ds.package_name}}::{{ds.module_name.upper()}}_DATA_WIDTH)
            else $error("Interface data width of %0d is incorrect. Shall be %0d bits", $bits({{cpuif.signal("odat")}}), {{ds.package_name}}::{{ds.module_name.upper()}}_DATA_WIDTH);
    end
`endif

{% endif -%}

// Request
always_comb begin
    cpuif_req = {{cpuif.signal("stb")}};
    cpuif_req_is_wr = {{cpuif.signal("we")}};
    cpuif_addr = {{cpuif.signal("adr")}};
    cpuif_wr_data = {{cpuif.signal("odat")}};
    for(int i=0; i<{{cpuif.data_width_bytes}}; i++) begin
        cpuif_wr_biten[i*8 +: 8] = {8{ {{-cpuif.signal("sel")}}[i]}};
    end
    {{cpuif.signal("stall")}} = {{cpuif.signal("stb")}} & ((cpuif_req_stall_rd) | (cpuif_req_stall_wr & {{cpuif.signal("we")}}));
end

// Response
always_comb begin
    {{cpuif.signal("ack")}} = cpuif_rd_ack | cpuif_wr_ack;
    {{cpuif.signal("idat")}} = cpuif_rd_data;
    {{cpuif.signal("err")}} = cpuif_rd_err | cpuif_wr_err;
end
