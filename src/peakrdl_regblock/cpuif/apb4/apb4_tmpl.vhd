-- Request
{%- macro apb4_reset() %}
    apb_is_active <= '0';
    cpuif_req <= '0';
    cpuif_req_is_wr <= '0';
    cpuif_addr <= (others => '0');
    cpuif_wr_data <= (others => '0');
    cpuif_wr_biten <= (others => '0');
{%- endmacro %}
process({{get_always_ff_event(cpuif.reset)}}) begin
    if {{get_resetsignal(cpuif.reset, asynch=True)}} then -- async reset
        {{- apb4_reset() | indent }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(cpuif.reset, asynch=False)}} then -- sync reset
            {{- apb4_reset() | indent(8) }}
        else
            if not apb_is_active then
                if {{cpuif.signal("psel")}} then
                    apb_is_active <= '1';
                    cpuif_req <= '1';
                    cpuif_req_is_wr <= {{cpuif.signal("pwrite")}};
                    {%- if cpuif.data_width_bytes == 1 %}
                    cpuif_addr <= {{cpuif.signal("paddr")}}({{cpuif.addr_width-1}} downto 0);
                    {%- else %}
                    cpuif_addr <= ({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}} => {{cpuif.signal("paddr")}}({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}}), others => '0');
                    {%- endif %}
                    cpuif_wr_data <= {{cpuif.signal("pwdata")}};
                    for i in {{cpuif.signal("pstrb")}}'RANGE loop
                        cpuif_wr_biten(i*8 + 7 downto i*8) <= (others => {{cpuif.signal("pstrb")}}(i));
                    end loop;
                end if;
            else
                cpuif_req <= '0';
                if cpuif_rd_ack or cpuif_wr_ack then
                    apb_is_active <= '0';
                end if;
            end if;
        end if;
    end if;
end process;

-- Response
{{cpuif.signal("pready")}} <= cpuif_rd_ack or cpuif_wr_ack;
{{cpuif.signal("prdata")}} <= cpuif_rd_data;
{{cpuif.signal("pslverr")}} <= cpuif_rd_err or cpuif_wr_err;
