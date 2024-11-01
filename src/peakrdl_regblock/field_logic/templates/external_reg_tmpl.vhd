{% if retime -%}

{%- macro ext_reg_reset() %}
        {{prefix}}.req <= {{ req_reset }};
        {{prefix}}.req_is_wr <= '0';
    {%- if has_sw_writable %}
        {{prefix}}.wr_data <= (others => '0');
        {{prefix}}.wr_biten <= (others => '0');
    {%- endif %}
{%- endmacro %}
process({{get_always_ff_event(resetsignal)}}) begin
    if {{get_resetsignal(resetsignal, asynch=True)}} then -- async reset
        {{- ext_reg_reset() }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(resetsignal, asynch=False)}} then -- sync reset
            {{- ext_reg_reset() | indent }}
        else
        {%- if has_sw_readable and has_sw_writable %}
            {{prefix}}.req <= {{strb}};
        {%- elif has_sw_readable and not has_sw_writable %}
            {{prefix}}.req <= {{strb}} when not decoded_req_is_wr else {{ req_reset }};
        {%- elif not has_sw_readable and has_sw_writable %}
            {{prefix}}.req <= {{strb}} when decoded_req_is_wr else {{ req_reset }};
        {%- endif %}
            {{prefix}}.req_is_wr <= decoded_req_is_wr;
        {%- if has_sw_writable %}
            {{prefix}}.wr_data <= decoded_wr_data{{bslice}};
            {{prefix}}.wr_biten <= decoded_wr_biten{{bslice}};
        {%- endif %}
        end if;
    end if;
end process;


{%- else -%}


{%- if has_sw_readable and has_sw_writable %}
{{prefix}}.req <= {{strb}};
{%- elif has_sw_readable and not has_sw_writable %}
{{prefix}}.req <= {{strb}} when not decoded_req_is_wr else {{ req_reset }};
{%- elif not has_sw_readable and has_sw_writable %}
{{prefix}}.req <= {{strb}} when decoded_req_is_wr else {{ req_reset }};
{%- endif %}
{{prefix}}.req_is_wr <= decoded_req_is_wr;
{%- if has_sw_writable %}
{{prefix}}.wr_data <= decoded_wr_data{{bslice}};
{{prefix}}.wr_biten <= decoded_wr_biten{{bslice}};
{%- endif %}


{%- endif %}
