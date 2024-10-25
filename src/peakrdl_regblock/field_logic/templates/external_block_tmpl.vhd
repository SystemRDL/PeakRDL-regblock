{% if retime -%}


{%- macro ext_block_reset() %}
    {{prefix}}.req <= '0;
    {{prefix}}.addr <= '0;
    {{prefix}}.req_is_wr <= '0;
    {{prefix}}.wr_data <= '0;
    {{prefix}}.wr_biten <= '0;
{%- endmacro %}
process({{get_always_ff_event(resetsignal)}}) begin
    -- TODO: double check this reset logic
    if {{get_resetsignal(resetsignal, asynch=True)}} then -- async reset
        {{- ext_block_reset() | indent }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(resetsignal, asynch=False)}} then -- sync reset
            {{- ext_block_reset() | indent(8) }}
        else
            {{prefix}}.req <= {{strb}};
            {{prefix}}.addr <= decoded_addr[{{addr_width-1}}:0];
            {{prefix}}.req_is_wr <= decoded_req_is_wr;
            {{prefix}}.wr_data <= decoded_wr_data;
            {{prefix}}.wr_biten <= decoded_wr_biten;
        end if;
    end if;
end process;


{%- else -%}


{{prefix}}.req <= {{strb}};
{{prefix}}.addr <= decoded_addr({{addr_width-1}} downto 0);
{{prefix}}.req_is_wr <= decoded_req_is_wr;
{{prefix}}.wr_data <= decoded_wr_data;
{{prefix}}.wr_biten <= decoded_wr_biten;


{%- endif %}