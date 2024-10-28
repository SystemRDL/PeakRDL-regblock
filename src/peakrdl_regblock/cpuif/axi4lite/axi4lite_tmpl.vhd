-- Max Outstanding Transactions: {{cpuif.max_outstanding}}

{%- macro axil_req_reset() %}
        axil_prev_was_rd <= '0';
        axil_arvalid <= '0';
        axil_araddr <= (others => '0');
        axil_awvalid <= '0';
        axil_awaddr <= (others => '0');
        axil_wvalid <= '0';
        axil_wdata <= (others => '0');
        axil_wstrb <= (others => '0');
        axil_n_in_flight <= (others => '0');
{%- endmacro %}
-- Transaction request acceptance
process({{get_always_ff_event(cpuif.reset)}}) begin
    if {{get_resetsignal(cpuif.reset, asynch=True)}} then -- async reset
        {{- axil_req_reset() }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(cpuif.reset, asynch=False)}} then -- sync reset
            {{- axil_req_reset() | indent }}
        else
            -- AR* acceptance register
            if axil_ar_accept then
                axil_prev_was_rd <= '1';
                axil_arvalid <= '0';
            end if;
            if {{cpuif.signal("arvalid")}} and {{cpuif.signal("arready")}} then
                axil_arvalid <= '1';
                axil_araddr <= {{cpuif.signal("araddr")}};
            end if;

            -- AW* & W* acceptance registers
            if axil_aw_accept  then
                axil_prev_was_rd <= '0';
                axil_awvalid <= '0';
                axil_wvalid <= '0';
            end if;
            if {{cpuif.signal("awvalid")}} and {{cpuif.signal("awready")}} then
                axil_awvalid <= '1';
                axil_awaddr <= {{cpuif.signal("awaddr")}};
            end if;
            if {{cpuif.signal("wvalid")}} and {{cpuif.signal("wready")}} then
                axil_wvalid <= '1';
                axil_wdata <= {{cpuif.signal("wdata")}};
                axil_wstrb <= {{cpuif.signal("wstrb")}};
            end if;

            -- Keep track of in-flight transactions
            if (axil_ar_accept or axil_aw_accept) and not axil_resp_acked then
                axil_n_in_flight <= axil_n_in_flight + 1;
            elsif not (axil_ar_accept or axil_aw_accept) and axil_resp_acked then
                axil_n_in_flight <= axil_n_in_flight - 1;
            end if;
        end if;
    end if;
end process;

process(all) begin
    {{cpuif.signal("arready")}} <= not axil_arvalid or axil_ar_accept;
    {{cpuif.signal("awready")}} <= not axil_awvalid or axil_aw_accept;
    {{cpuif.signal("wready")}} <= not axil_wvalid or axil_aw_accept;
end process;

-- Request dispatch
process(all) begin
    cpuif_wr_data <= axil_wdata;
    for i in axil_wstrb'RANGE loop
        cpuif_wr_biten(i*8 + 7 downto i*8) <= (others => axil_wstrb(i));
    end loop;
    cpuif_req <= '0';
    cpuif_req_is_wr <= '0';
    cpuif_addr <= (others => '0');
    axil_ar_accept <= '0';
    axil_aw_accept <= '0';

    if axil_n_in_flight < to_unsigned({{cpuif.max_outstanding}}, {{clog2(cpuif.max_outstanding+1)}}) then
        -- Can safely issue more transactions without overwhelming response buffer
        if axil_arvalid and not axil_prev_was_rd then
            cpuif_req <= '1';
            cpuif_req_is_wr <= '0';
            {%- if cpuif.data_width_bytes == 1 %}
            cpuif_addr <= axil_araddr;
            {%- else %}
            cpuif_addr <= ({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}} => axil_araddr({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}}), others => '0');
            {%- endif %}
            if not cpuif_req_stall_rd then
                axil_ar_accept <= '1';
            end if;
        elsif axil_awvalid and axil_wvalid then
            cpuif_req <= '1';
            cpuif_req_is_wr <= '1';
            {%- if cpuif.data_width_bytes == 1 %}
            cpuif_addr <= axil_awaddr;
            {%- else %}
            cpuif_addr <= ({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}} => axil_awaddr({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}}), others => '0');
            {%- endif %}
            if not cpuif_req_stall_wr then
                axil_aw_accept <= '1';
            end if;
        elsif axil_arvalid then
            cpuif_req <= '1';
            cpuif_req_is_wr <= '0';
            {%- if cpuif.data_width_bytes == 1 %}
            cpuif_addr <= axil_araddr;
            {%- else %}
            cpuif_addr <= ({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}} => axil_araddr({{cpuif.addr_width-1}} downto {{clog2(cpuif.data_width_bytes)}}), others => '0');
            {%- endif %}
            if not cpuif_req_stall_rd then
                axil_ar_accept <= '1';
            end if;
        end if;
    end if;
end process;

{%- macro axil_resp_reset() %}
        {{cpuif.signal("rvalid")}} <= '0';
        {{cpuif.signal("rresp")}} <= (others => '0');
        {{cpuif.signal("rdata")}} <= (others => '0');
        {{cpuif.signal("bvalid")}} <= '0';
        {{cpuif.signal("bresp")}} <= (others => '0');
{%- endmacro %}
-- AXI4-Lite Response Logic
{%- if cpuif.resp_buffer_size == 1 %}
process({{get_always_ff_event(cpuif.reset)}}) begin
    if {{get_resetsignal(cpuif.reset, asynch=True)}} then -- async reset
        {{- axil_resp_reset() }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(cpuif.reset, asynch=False)}} then -- sync reset
            {{- axil_resp_reset() | indent }}
        else
            if {{cpuif.signal("rvalid")}} and {{cpuif.signal("rready")}} then
                {{cpuif.signal("rvalid")}} <= '0';
            end

            if {{cpuif.signal("bvalid")}} and {{cpuif.signal("bready")}} then
                {{cpuif.signal("bvalid")}} <= '0';
            end

            if cpuif_rd_ack then
                {{cpuif.signal("rvalid")}} <= '1';
                {{cpuif.signal("rdata")}} <= cpuif_rd_data;
                if cpuif_rd_err then
                    {{cpuif.signal("rresp")}} <= "10"; -- SLVERR
                else
                    {{cpuif.signal("rresp")}} <= "00"; -- OKAY
                end if;
            end

            if cpuif_wr_ack then
                {{cpuif.signal("bvalid")}} <= '1';
                if cpuif_wr_err then
                    {{cpuif.signal("bresp")}} <= "10"; -- SLVERR
                else
                    {{cpuif.signal("bresp")}} <= "00"; -- OKAY
                end if;
            end if;
        end if;
    end if;
end process;

process(all) begin
    axil_resp_acked <= '0';
    if {{cpuif.signal("rvalid")}} and {{cpuif.signal("rready")}} then
        axil_resp_acked <= '1';
    end if;
    if {{cpuif.signal("bvalid")}} and {{cpuif.signal("bready")}} then
        axil_resp_acked <= '1';
    end if;
end

{%- else %}
{%- if not is_pow2(cpuif.resp_buffer_size) %}
-- axil_resp_buffer is intentionally padded to the next power of two despite
-- only requiring {{cpuif.resp_buffer_size}} entries.
-- This is to avoid quirks in some tools that cannot handle indexing into a non-power-of-2 array.
-- Unused entries are expected to be optimized away
{% endif %}

{%- macro axil_resp_buffer_reset() %}
        for i in axil_resp_buffer'RANGE loop
            axil_resp_buffer(i).is_wr <= '0';
            axil_resp_buffer(i).err <= '0';
            axil_resp_buffer(i).rdata <= (others => '0');
        end loop;
        axil_resp_wptr <= (others => '0');
        axil_resp_rptr <= (others => '0');
{%- endmacro %}
process({{get_always_ff_event(cpuif.reset)}}) begin
    if {{get_resetsignal(cpuif.reset, asynch=True)}} then -- async reset
        {{- axil_resp_buffer_reset() }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(cpuif.reset, asynch=False)}} then -- sync reset
            {{- axil_resp_buffer_reset() | indent }}
        else
            -- Store responses in buffer until AXI response channel accepts them
            if cpuif_rd_ack or cpuif_wr_ack then
                if cpuif_rd_ack then
                    axil_resp_buffer(to_integer(axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).is_wr <= '0';
                    axil_resp_buffer(to_integer(axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).err <= cpuif_rd_err;
                    axil_resp_buffer(to_integer(axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).rdata <= cpuif_rd_data;

                elsif cpuif_wr_ack then
                    axil_resp_buffer(to_integer(axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).is_wr <= '1';
                    axil_resp_buffer(to_integer(axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).err <= cpuif_wr_err;
                end if;
                {%- if is_pow2(cpuif.resp_buffer_size) %}
                axil_resp_wptr <= axil_resp_wptr + 1;
                {%- else %}
                if axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) = {{cpuif.resp_buffer_size-1}} then
                    axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) <= (others => '0');
                    axil_resp_wptr({{clog2(cpuif.resp_buffer_size)}}) <= not axil_resp_wptr({{clog2(cpuif.resp_buffer_size)}});
                else
                    axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) <= axil_resp_wptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) + 1;
                end if;
                {%- endif %}
            end if;

            -- Advance read pointer when acknowledged
            if axil_resp_acked then
                {%- if is_pow2(cpuif.resp_buffer_size) %}
                axil_resp_rptr <= axil_resp_rptr + 1;
                {%- else %}
                if axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) = {{cpuif.resp_buffer_size-1}} then
                    axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) <= (others => '0');
                    axil_resp_rptr({{clog2(cpuif.resp_buffer_size)}}) <= not axil_resp_rptr({{clog2(cpuif.resp_buffer_size)}});
                else
                    axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) <= axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0) + 1;
                end if;
                {%- endif %}
            end if;
        end if;
    end if;
end process;

process(all) begin
    axil_resp_acked <= '0';
    {{cpuif.signal("bvalid")}} <= '0';
    {{cpuif.signal("rvalid")}} <= '0';
    if axil_resp_rptr /= axil_resp_wptr then
        if axil_resp_buffer(to_integer(axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).is_wr then
            {{cpuif.signal("bvalid")}} <= '1';
            if {{cpuif.signal("bready")}} then
                axil_resp_acked <= '1';
            end if;
        else
            {{cpuif.signal("rvalid")}} <= '1';
            if {{cpuif.signal("rready")}} then
                axil_resp_acked <= '1';
            end if;
        end if;
    end if;

    {{cpuif.signal("rdata")}} <= axil_resp_buffer(to_integer(axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).rdata;
    if axil_resp_buffer(to_integer(axil_resp_rptr({{clog2(cpuif.resp_buffer_size)-1}} downto 0))).err then
        {{cpuif.signal("bresp")}} <= "10";
        {{cpuif.signal("rresp")}} <= "10";
    else
        {{cpuif.signal("bresp")}} <= "00";
        {{cpuif.signal("rresp")}} <= "00";
    end if;
end process;
{%- endif %}
