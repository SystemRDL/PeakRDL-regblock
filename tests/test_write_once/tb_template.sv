{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    cb.hwif_in.r3.f.swwe <= '0;
    ##1;
    cb.rst <= '0;
    ##1;

    // r1: basic write onec (rw1)
    @cb;
    cpuif.assert_read('h0, 'h11);
    cpuif.write      ('h0, 'h12);
    cpuif.assert_read('h0, 'h12);
    cpuif.write      ('h0, 'h13); // ignored
    cpuif.assert_read('h0, 'h12);

    // r2: write once is observed via hw signal
    @cb;
    assert(cb.hwif_out.r2.f.value == 8'h22);
    cpuif.write      ('h1, 'h23);
    @cb;
    assert(cb.hwif_out.r2.f.value == 8'h23);
    cpuif.write      ('h1, 'h24); // ignored
    @cb;
    assert(cb.hwif_out.r2.f.value == 8'h23);

    // r3: write blocked by swwe does not consume the write-once
    @cb;
    cpuif.assert_read('h2, 'h33);
    cpuif.write      ('h2, 'h34); // blocked by swwe
    cpuif.assert_read('h2, 'h33);
    @cb;
    cb.hwif_in.r3.f.swwe <= '1;
    @cb;
    cpuif.write      ('h2, 'h35);
    cpuif.assert_read('h2, 'h35);
    cpuif.write      ('h2, 'h36); // ignored
    cpuif.assert_read('h2, 'h35);

    // r4: write once without a reset value for field
    @cb;
    cpuif.write      ('h3, 'h43);
    cpuif.assert_read('h3, 'h43);
    cpuif.write      ('h3, 'h44); // ignored
    cpuif.assert_read('h3, 'h43);

    // r5: write once in a write-buffered register
    @cb;
    cpuif.assert_read('h4, 'h55);
    cpuif.write      ('h4, 'h56);
    cpuif.assert_read('h4, 'h56);
    cpuif.write      ('h4, 'h57); // ignored
    cpuif.assert_read('h4, 'h56);

    // reset restores the write-once
    @cb;
    cb.rst <= '1;
    ##2;
    cb.rst <= '0;
    ##1;
    @cb;
    cpuif.assert_read('h0, 'h11);
    cpuif.write      ('h0, 'h14);
    cpuif.assert_read('h0, 'h14);
    cpuif.write      ('h0, 'h15); // ignored
    cpuif.assert_read('h0, 'h14);

{% endblock %}