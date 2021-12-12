{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    cpuif.write('h0, 'h00);
    @cb;
    assert(cb.hwif_out.r1.f.anded == 1'b0);
    assert(cb.hwif_out.r1.f.ored  == 1'b0);
    assert(cb.hwif_out.r1.f.xored == 1'b0);

    cpuif.write('h0, 'h01);
    @cb;
    assert(cb.hwif_out.r1.f.anded == 1'b0);
    assert(cb.hwif_out.r1.f.ored  == 1'b1);
    assert(cb.hwif_out.r1.f.xored == 1'b1);

    cpuif.write('h0, 'h02);
    @cb;
    assert(cb.hwif_out.r1.f.anded == 1'b0);
    assert(cb.hwif_out.r1.f.ored  == 1'b1);
    assert(cb.hwif_out.r1.f.xored == 1'b1);

    cpuif.write('h0, 'h03);
    @cb;
    assert(cb.hwif_out.r1.f.anded == 1'b0);
    assert(cb.hwif_out.r1.f.ored  == 1'b1);
    assert(cb.hwif_out.r1.f.xored == 1'b0);

    cpuif.write('h0, 'hFE);
    @cb;
    assert(cb.hwif_out.r1.f.anded == 1'b0);
    assert(cb.hwif_out.r1.f.ored  == 1'b1);
    assert(cb.hwif_out.r1.f.xored == 1'b1);

    cpuif.write('h0, 'hFF);
    @cb;
    assert(cb.hwif_out.r1.f.anded == 1'b1);
    assert(cb.hwif_out.r1.f.ored  == 1'b1);
    assert(cb.hwif_out.r1.f.xored == 1'b0);
{% endblock %}
