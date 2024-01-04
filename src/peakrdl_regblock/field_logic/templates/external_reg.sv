{% if retime -%}


always_ff {{get_always_ff_event(resetsignal)}} begin
    if({{get_resetsignal(resetsignal)}}) begin
        {{prefix}}.req <= '0;
        {{prefix}}.req_is_wr <= '0;
    {%- if has_sw_writable %}
        {{prefix}}.wr_data <= '0;
        {{prefix}}.wr_biten <= '0;
    {%- endif %}
    end else begin
    {%- if has_sw_readable and has_sw_writable %}
        {{prefix}}.req <= {{strb}};
    {%- elif has_sw_readable and not has_sw_writable %}
        {{prefix}}.req <= !decoded_req_is_wr ? {{strb}} : '0;
    {%- elif not has_sw_readable and has_sw_writable %}
        {{prefix}}.req <= decoded_req_is_wr ? {{strb}} : '0;
    {%- endif %}
        {{prefix}}.req_is_wr <= decoded_req_is_wr;
    {%- if has_sw_writable %}
        {{prefix}}.wr_data <= decoded_wr_data{{bslice}};
        {{prefix}}.wr_biten <= decoded_wr_biten{{bslice}};
    {%- endif %}
    end
end


{%- else -%}


{%- if has_sw_readable and has_sw_writable %}
assign {{prefix}}.req = {{strb}};
{%- elif has_sw_readable and not has_sw_writable %}
assign {{prefix}}.req = !decoded_req_is_wr ? {{strb}} : '0;
{%- elif not has_sw_readable and has_sw_writable %}
assign {{prefix}}.req = decoded_req_is_wr ? {{strb}} : '0;
{%- endif %}
assign {{prefix}}.req_is_wr = decoded_req_is_wr;
{%- if has_sw_writable %}
assign {{prefix}}.wr_data = decoded_wr_data{{bslice}};
assign {{prefix}}.wr_biten = decoded_wr_biten{{bslice}};
{%- endif %}


{%- endif %}
