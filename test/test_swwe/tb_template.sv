{% extends "lib/templates/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // r1 swwe = true
    cpuif.assert_read('h1, 'h11);
    cb.hwif_in.r1.f.swwe <= '0;
    cpuif.write      ('h1, 'h12);
    cpuif.assert_read('h1, 'h11);
    cb.hwif_in.r1.f.swwe <= '1;
    cpuif.write      ('h1, 'h13);
    cpuif.assert_read('h1, 'h13);

    // r2 swwel = true
    cpuif.assert_read('h2, 'h22);
    cb.hwif_in.r2.f.swwel <= '1;
    cpuif.write      ('h2, 'h23);
    cpuif.assert_read('h2, 'h22);
    cb.hwif_in.r2.f.swwel <= '0;
    cpuif.write      ('h2, 'h24);
    cpuif.assert_read('h2, 'h24);

    // r3 swwe = lock.r3_swwe
    cpuif.assert_read('h3, 'h33);
    cpuif.write      ('h0, 'h0);
    cpuif.write      ('h3, 'h32);
    cpuif.assert_read('h3, 'h33);
    cpuif.write      ('h0, 'h1);
    cpuif.write      ('h3, 'h34);
    cpuif.assert_read('h3, 'h34);

    // r4 swwel = lock.r4_swwel
    cpuif.assert_read('h4, 'h44);
    cpuif.write      ('h0, 'h2);
    cpuif.write      ('h4, 'h40);
    cpuif.assert_read('h4, 'h44);
    cpuif.write      ('h0, 'h0);
    cpuif.write      ('h4, 'h45);
    cpuif.assert_read('h4, 'h45);

    // r5 swwe = r3->swwe = lock.r3_swwe
    cpuif.assert_read('h5, 'h55);
    cpuif.write      ('h0, 'h0);
    cpuif.write      ('h5, 'h52);
    cpuif.assert_read('h5, 'h55);
    cpuif.write      ('h0, 'h1);
    cpuif.write      ('h5, 'h54);
    cpuif.assert_read('h5, 'h54);

    // r6 swwe = r4->swwel = lock.r4_swwel
    cpuif.assert_read('h6, 'h66);
    cpuif.write      ('h0, 'h0);
    cpuif.write      ('h6, 'h60);
    cpuif.assert_read('h6, 'h66);
    cpuif.write      ('h0, 'h2);
    cpuif.write      ('h6, 'h65);
    cpuif.assert_read('h6, 'h65);

{% endblock %}
