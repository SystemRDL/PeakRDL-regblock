process(clk) begin
    if rising_edge(clk) then
        if {{rbuf.get_trigger(node)}} then
            {{get_assignments(node)|indent(12)}}
        end if;
    end if;
end process;
