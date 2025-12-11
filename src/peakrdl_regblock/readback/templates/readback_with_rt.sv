function automatic bit [{{low_addr_width-1}}:0] ad_low(bit [{{ds.addr_width-1}}:0] addr);
    return addr[{{low_addr_width-1}}:0];
endfunction
function automatic bit [{{high_addr_width-1}}:0] ad_hi(bit [{{ds.addr_width-1}}:0] addr);
    return addr[{{ds.addr_width-1}}:{{low_addr_width}}];
endfunction

// readback stage 1
logic [{{cpuif.data_width-1}}:0] readback_data_rt_c[{{2 ** high_addr_width}}];
always_comb begin
    automatic logic [{{cpuif.data_width-1}}:0] readback_data_var[{{2 ** high_addr_width}}];
    for(int i=0; i<{{2 ** high_addr_width}}; i++) readback_data_var[i] = '0;
    {{readback_mux|indent}}
    readback_data_rt_c = readback_data_var;
end

logic [{{cpuif.data_width-1}}:0] readback_data_rt[{{2 ** high_addr_width}}];
logic readback_done_rt;
logic readback_err_rt;
logic [{{ds.addr_width-1}}:0] readback_addr_rt;
always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        for(int i=0; i<{{2 ** high_addr_width}}; i++) readback_data_rt[i] <= '0;
        readback_done_rt <= '0;
        readback_err_rt <= '0;
        readback_addr_rt <= '0;
    end else begin
        readback_data_rt <= readback_data_rt_c;
        readback_err_rt <= decoded_err;
        {%- if ds.has_external_addressable %}
        readback_done_rt <= decoded_req & ~decoded_req_is_wr & ~decoded_req_is_external;
        {%- else %}
        readback_done_rt <= decoded_req & ~decoded_req_is_wr;
        {%- endif %}
        readback_addr_rt <= rd_mux_addr;
    end
end

{% if ds.has_external_block %}
logic [{{cpuif.data_width-1}}:0] readback_ext_block_data_rt_c;
logic readback_is_ext_block_c;
always_comb begin
    automatic logic [{{cpuif.data_width-1}}:0] readback_data_var;
    automatic logic is_external_block_var;
    readback_data_var = '0;
    is_external_block_var = '0;
    {{ext_block_readback_mux|indent}}
    readback_ext_block_data_rt_c = readback_data_var;
    readback_is_ext_block_c = is_external_block_var;
end

logic [{{cpuif.data_width-1}}:0] readback_ext_block_data_rt;
logic readback_is_ext_block;
always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        readback_ext_block_data_rt <= '0;
        readback_is_ext_block <= '0;
    end else begin
        readback_ext_block_data_rt <= readback_ext_block_data_rt_c;
        readback_is_ext_block <= readback_is_ext_block_c;
    end
end
{% endif %}

// readback stage 2
always_comb begin
    {%- if ds.has_external_block %}
    if(readback_is_ext_block) begin
        readback_data = readback_ext_block_data_rt;
    end else begin
        readback_data = readback_data_rt[readback_addr_rt[{{ds.addr_width-1}}:{{low_addr_width}}]];
    end
    {%- else %}
    readback_data = readback_data_rt[readback_addr_rt[{{ds.addr_width-1}}:{{low_addr_width}}]];
    {%- endif %}
    readback_done = readback_done_rt;
    {%- if ds.err_if_bad_addr or ds.err_if_bad_rw %}
    readback_err = readback_err_rt;
    {%- else %}
    readback_err = '0;
    {%- endif %}
end
