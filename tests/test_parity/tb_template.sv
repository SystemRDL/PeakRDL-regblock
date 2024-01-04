{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    fork
        begin
            repeat(50) begin
                automatic int i = $urandom_range(7,0);
                cpuif.write('h0, $urandom());
                cpuif.write('h1000 + i*4, $urandom());
            end
        end
        begin
            forever begin
                assert(cb.parity_error != 1'b1);
                @cb;
            end
        end
    join_any
    disable fork;

    cpuif.write('h0, 'd0);
    assign dut.field_storage.r1.f1.value = 16'd1;
    deassign dut.field_storage.r1.f1.value;
    @cb;
    @cb;
    assert(cb.parity_error == 1'b1);
    cpuif.write('h0, 'd0);
    @cb;
    @cb;
    assert(cb.parity_error == 1'b0);

{% endblock %}
