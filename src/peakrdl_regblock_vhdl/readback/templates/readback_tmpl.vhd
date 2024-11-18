{% if array_assignments is not none %}
-- Assign readback values to a flattened array
{{array_assignments}}


{%- if ds.retime_read_fanin %}

-- fanin stage
gen_fanin: for g in 0 to {{fanin_loop_iter-1}} generate
    process (all)
        variable readback_data_var : std_logic_vector({{cpuif.data_width-1}} downto 0);
    begin
        readback_data_var := (others => '0');
        for i in g*{{fanin_stride}} to (g+1)*{{fanin_stride}}-1 loop
            readback_data_var := readback_data_var or readback_array(i);
        end loop;
        readback_array_c(g) <= readback_data_var;
    end process;
end generate;
{%- if fanin_residual_stride == 1 %}
readback_array_c({{fanin_array_size-1}}) <= readback_array({{array_size-1}});
{%- elif fanin_residual_stride > 1 %}
process (all)
    variable readback_data_var : std_logic_vector({{cpuif.data_width-1}} downto 0);
begin
    readback_data_var := (others => '0');
    for i in {{(fanin_array_size-1) * fanin_stride}} to {{array_size-1}} loop
        readback_data_var := readback_data_var or readback_array(i);
    end loop;
    readback_array_c({{fanin_array_size-1}}) <= readback_data_var;
end process;
{%- endif %}

process({{get_always_ff_event(cpuif.reset)}}) begin
    if {{get_resetsignal(cpuif.reset, asynch=True)}} then -- async reset
        readback_array_r <= (others => {{cpuif.data_width}}x"0");
        readback_done_r <= '0';
    elsif rising_edge(clk) then
        if {{get_resetsignal(cpuif.reset, asynch=False)}} then -- sync reset
            readback_array_r <= (others => {{cpuif.data_width}}x"0");
            readback_done_r <= '0';
        else
            readback_array_r <= readback_array_c;
            {%- if ds.has_external_addressable %}
            readback_done_r <= decoded_req and not decoded_req_is_wr and not decoded_strb_is_external;
            {%- else %}
            readback_done_r <= decoded_req and not decoded_req_is_wr;
            {%- endif %}
        end if;
    end if;
end process;

-- Reduce the array
process(all)
    variable readback_data_var : std_logic_vector({{cpuif.data_width-1}} downto 0) := (others => '0');
begin
    readback_done <= readback_done_r;
    readback_err <= '0';
    readback_data_var := (others => '0');
    for i in 0 to {{fanin_array_size-1}} loop
        readback_data_var := readback_data_var or readback_array_r(i);
    end loop;
    readback_data <= readback_data_var;
end process;

{%- else %}

-- Reduce the array
process(all)
    variable readback_data_var : std_logic_vector({{cpuif.data_width-1}} downto 0) := (others => '0');
begin
    {%- if ds.has_external_addressable %}
    readback_done <= decoded_req and not decoded_req_is_wr and not decoded_strb_is_external;
    {%- else %}
    readback_done <= decoded_req and not decoded_req_is_wr;
    {%- endif %}
    readback_err <= '0';
    readback_data_var := (others => '0');
    for i in readback_array'RANGE loop
        readback_data_var := readback_data_var or readback_array(i);
    end loop;
    readback_data <= readback_data_var;
end process;
{%- endif %}



{%- else %}
readback_done <= decoded_req and not decoded_req_is_wr;
readback_data <= '0';
readback_err <= '0';
{% endif %}
