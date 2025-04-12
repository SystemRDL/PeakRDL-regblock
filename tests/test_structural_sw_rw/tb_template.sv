{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // Assert value via frontdoor
    cpuif.assert_read(0, 32'h8000_0042);
    for(int i=0; i<2*3*4; i++) begin
        cpuif.assert_read('h10+i*8, 32'h8000_0023);
    end
    cpuif.assert_read('h1000, 32'h8000_0011);
    for(int i=0; i<33; i++) begin
        cpuif.assert_read('h2000 +i*4, 32'h0000_0010);
    end

    // Assert via hwif
    assert(cb.hwif_out.r0.a.value == 'h42);
    assert(cb.hwif_out.r0.b.value == 'h0);
    assert(cb.hwif_out.r0.c.value == 'h1);
    foreach(cb.hwif_out.r1[x, y, z]) begin
        assert(cb.hwif_out.r1[x][y][z].a.value == 'h23);
        assert(cb.hwif_out.r1[x][y][z].b.value == 'h0);
        assert(cb.hwif_out.r1[x][y][z].c.value == 'h1);
    end
    assert(cb.hwif_out.r2.a.value == 'h11);
    assert(cb.hwif_out.r2.b.value == 'h0);
    assert(cb.hwif_out.r2.c.value == 'h1);

    // Write values
    cpuif.write(0, 32'h8000_0002);
    for(int i=0; i<2*3*4; i++) begin
        cpuif.write('h10+i*8, i+'h110a);
    end
    cpuif.write('h1000, 32'h0000_0000);
    for(int i=0; i<33; i++) begin
        cpuif.write('h2000 +i*4, i << 4);
    end

    // Assert value via frontdoor
    cpuif.assert_read(0, 32'h8000_0002);
    for(int i=0; i<2*3*4; i++) begin
        cpuif.assert_read('h10+i*8, i+'h10a);
    end
    cpuif.assert_read('h1000, 32'h0000_0000);
    for(int i=0; i<33; i++) begin
        cpuif.assert_read('h2000 +i*4, (i << 4) & 'hF0);
    end

    // Assert via hwif
    assert(cb.hwif_out.r0.a.value == 'h02);
    assert(cb.hwif_out.r0.b.value == 'h0);
    assert(cb.hwif_out.r0.c.value == 'h1);
    foreach(cb.hwif_out.r1[x, y, z]) begin
        assert(cb.hwif_out.r1[x][y][z].a.value == x*12+y*4+z+10);
        assert(cb.hwif_out.r1[x][y][z].b.value == 'h1);
        assert(cb.hwif_out.r1[x][y][z].c.value == 'h0);
    end
    assert(cb.hwif_out.r2.a.value == 'h0);
    assert(cb.hwif_out.r2.b.value == 'h0);
    assert(cb.hwif_out.r2.c.value == 'h0);

    // rw_reg
    cpuif.assert_read('h3000, 0);
    cpuif.write('h3000, 'h4DEAB000);
    @cb;
    assert(cb.hwif_out.rw_reg.f1.value == 8'hAB);
    assert(cb.hwif_out.rw_reg.f2.value == 11'h4DE);
    cpuif.assert_read('h3000, 'h4DEAB000);

    // rw_reg_lsb0
    cpuif.assert_read('h3004, 0);
    cpuif.write('h3004, 'h4DEAB000);
    @cb;
    assert(`bitswap(cb.hwif_out.rw_reg_lsb0.f1.value) == 8'hAB);
    assert(`bitswap(cb.hwif_out.rw_reg_lsb0.f2.value) == 11'h4DE);
    cpuif.assert_read('h3004, 'h4DEAB000);
{% endblock %}
