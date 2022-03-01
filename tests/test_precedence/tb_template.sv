{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Always write both fields from hardware
    cb.hwif_in.r1.f_sw.next <= '0;
    cb.hwif_in.r1.f_sw.we <= '1;
    cb.hwif_in.r1.f_hw.next <= '0;
    cb.hwif_in.r1.f_hw.we <= '1;
    @cb;
    @cb;

    cpuif.assert_read('h0, 'b00);
    cpuif.assert_read('h4, 'h00);

    cpuif.write('h0, 'b11);
    cpuif.write('h0, 'b11);
    cpuif.write('h0, 'b11);
    cpuif.assert_read('h0, 'h00);
    cpuif.assert_read('h4, 'h03);

{% endblock %}
