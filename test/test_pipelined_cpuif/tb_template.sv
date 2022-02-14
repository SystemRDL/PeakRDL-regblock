{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Write all regs in parallel burst
    for(int i=0; i<64; i++) begin
        fork
            automatic int i_fk = i;
            begin
                cpuif.write(i_fk*4, i_fk + 32'h12340000);
            end
        join_none
    end
    wait fork;

    // Verify HW value
    @cb;
    for(int i=0; i<64; i++) begin
        assert(cb.hwif_out.x[i].x.value == i + 32'h12340000)
            else $error("hwif_out.x[i] == 0x%0x. Expected 0x%0x", cb.hwif_out.x[i].x.value, i + 32'h12340000);
    end

    // Read all regs in parallel burst
    for(int i=0; i<64; i++) begin
        fork
            automatic int i_fk = i;
            begin
                cpuif.assert_read(i_fk*4, i_fk + 32'h12340000);
            end
        join_none
    end
    wait fork;

    // Mix read/writes
    for(int i=0; i<64; i++) begin
        fork
            automatic int i_fk = i;
            begin
                cpuif.write(i_fk*4, i_fk + 32'h56780000);
                cpuif.assert_read(i_fk*4, i_fk + 32'h56780000);
            end
        join_none
    end
    wait fork;

{% endblock %}
