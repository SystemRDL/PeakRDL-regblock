{% extends "lib/templates/tb_base.sv" %}

{% block seq %}
    cb.hwif_in.r3.f.wel <= 1;
    ##1;
    cb.rst <= '0;
    ##1;

    // r1 - sw=rw; hw=rw; we; // Storage element
    cpuif.assert_read('h0, 10);
    assert(cb.hwif_out.r1.f.value == 10);

    cpuif.write('h0, 11);
    cpuif.assert_read('h0, 11);
    assert(cb.hwif_out.r1.f.value == 11);

    cb.hwif_in.r1.f.value <= 9;
    cpuif.assert_read('h0, 11);
    assert(cb.hwif_out.r1.f.value == 11);
    cb.hwif_in.r1.f.value <= 12;
    cb.hwif_in.r1.f.we <= 1;
    @cb;
    cb.hwif_in.r1.f.value <= 0;
    cb.hwif_in.r1.f.we <= 0;
    cpuif.assert_read('h0, 12);
    assert(cb.hwif_out.r1.f.value == 12);


    // r2 - sw=rw; hw=r; // Storage element
    cpuif.assert_read('h1, 20);
    assert(cb.hwif_out.r2.f.value == 20);

    cpuif.write('h1, 21);
    cpuif.assert_read('h1, 21);
    assert(cb.hwif_out.r2.f.value == 21);


    // r3 - sw=rw; hw=w; wel; // Storage element
    cpuif.assert_read('h2, 30);

    cpuif.write('h2, 31);
    cpuif.assert_read('h2, 31);

    cb.hwif_in.r3.f.value <= 29;
    cpuif.assert_read('h2, 31);
    cb.hwif_in.r3.f.value <= 32;
    cb.hwif_in.r3.f.wel <= 0;
    @cb;
    cb.hwif_in.r3.f.value <= 0;
    cb.hwif_in.r3.f.wel <= 1;
    cpuif.assert_read('h2, 32);


    // r4 - sw=rw; hw=na; // Storage element
    cpuif.assert_read('h3, 40);
    cpuif.write('h3, 41);
    cpuif.assert_read('h3, 41);


    // r5 - sw=r; hw=rw; we; // Storage element
    cpuif.assert_read('h4, 50);
    assert(cb.hwif_out.r5.f.value == 50);

    cpuif.write('h4, 51);
    cpuif.assert_read('h4, 50);
    assert(cb.hwif_out.r5.f.value == 50);

    cb.hwif_in.r5.f.value <= 9;
    cpuif.assert_read('h4, 50);
    assert(cb.hwif_out.r5.f.value == 50);
    cb.hwif_in.r5.f.value <= 52;
    cb.hwif_in.r5.f.we <= 1;
    @cb;
    cb.hwif_in.r5.f.value <= 0;
    cb.hwif_in.r5.f.we <= 0;
    cpuif.assert_read('h4, 52);
    assert(cb.hwif_out.r5.f.value == 52);


    // r6 - sw=r; hw=r; // Wire/Bus - constant value
    cpuif.assert_read('h5, 60);
    assert(cb.hwif_out.r6.f.value == 60);
    cpuif.write('h5, 61);
    cpuif.assert_read('h5, 60);
    assert(cb.hwif_out.r6.f.value == 60);


    // r7 - sw=r; hw=w; // Wire/Bus - hardware assigns value
    cpuif.assert_read('h6, 0);
    cb.hwif_in.r7.f.value = 70;
    cpuif.assert_read('h6, 70);
    cpuif.write('h6, 71);
    cpuif.assert_read('h6, 70);


    // r8 - sw=r; hw=na; // Wire/Bus - constant value
    cpuif.assert_read('h7, 80);
    cpuif.write('h7, 81);
    cpuif.assert_read('h7, 80);


    // r9 - sw=w; hw=rw; we; // Storage element
    cpuif.assert_read('h8, 0);
    assert(cb.hwif_out.r9.f.value == 90);

    cpuif.write('h8, 91);
    cpuif.assert_read('h8, 0);
    assert(cb.hwif_out.r9.f.value == 91);

    cb.hwif_in.r9.f.value <= 89;
    cpuif.assert_read('h8, 0);
    assert(cb.hwif_out.r9.f.value == 91);
    cb.hwif_in.r9.f.value <= 92;
    cb.hwif_in.r9.f.we <= 1;
    @cb;
    cb.hwif_in.r9.f.value <= 0;
    cb.hwif_in.r9.f.we <= 0;
    cpuif.assert_read('h8, 0);
    assert(cb.hwif_out.r9.f.value == 92);


    // r10 - sw=w; hw=r; // Storage element
    cpuif.assert_read('h9, 0);
    assert(cb.hwif_out.r10.f.value == 100);

    cpuif.write('h9, 101);
    cpuif.assert_read('h9, 0);
    assert(cb.hwif_out.r10.f.value == 101);

{% endblock %}
