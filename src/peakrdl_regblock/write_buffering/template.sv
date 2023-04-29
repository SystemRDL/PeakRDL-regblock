always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        {{wbuf_prefix}}.pending <= '0;
        {{wbuf_prefix}}.data <= '0;
        {{wbuf_prefix}}.biten <= '0;
        {%- if is_own_trigger %}
        {{wbuf_prefix}}.trigger_q <= '0;
        {%- endif %}
    end else begin
        {%- for segment in segments %}
        if({{segment.strobe}} && decoded_req_is_wr) begin
            {{wbuf_prefix}}.pending <= '1;
            {%- if node.inst.is_msb0_order %}
            {{wbuf_prefix}}.data{{segment.bslice}} <= decoded_wr_data_bswap;
            {{wbuf_prefix}}.biten{{segment.bslice}} <= decoded_wr_biten_bswap;
            {%- else %}
            {{wbuf_prefix}}.data{{segment.bslice}} <= ({{wbuf_prefix}}.data{{segment.bslice}} & ~decoded_wr_biten{{segment.bslice}}) | (decoded_wr_data{{segment.bslice}} & decoded_wr_biten{{segment.bslice}});
            {{wbuf_prefix}}.biten{{segment.bslice}} <= decoded_wr_biten | {{wbuf_prefix}}.biten{{segment.bslice}};
            {%- endif %}
        end
        {%- endfor %}
        {% if is_own_trigger %}
        {{wbuf_prefix}}.trigger_q <= {{wbuf.get_raw_trigger(node)}};
        {%- endif %}
        if({{wbuf.get_trigger(node)}}) begin
            {{wbuf_prefix}}.pending <= '0;
            {{wbuf_prefix}}.data <= '0;
            {{wbuf_prefix}}.biten <= '0;
        end
    end
end
