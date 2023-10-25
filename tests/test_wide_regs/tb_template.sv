{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // rw_reg1
    assert(cb.hwif_out.rw_reg1.f1.value == 0);
    assert(cb.hwif_out.rw_reg1.f2.value == 0);
    assert(cb.hwif_out.rw_reg1.f3.value == 0);
    assert(cb.hwif_out.rw_reg1.f4.value == 0);
    cpuif.write('h0, 'h1234);
    cpuif.write('h2, 'h5678);
    cpuif.write('h4, 'h9ABC);
    cpuif.write('h6, 'hDEF1);
    @cb;
    assert(cb.hwif_out.rw_reg1.f1.value == 8'h34);
    assert(cb.hwif_out.rw_reg1.f2.value == 3'h1);
    assert(cb.hwif_out.rw_reg1.f3.value == 1'h1);
    assert(cb.hwif_out.rw_reg1.f4.value == 8'h9A);
    cpuif.assert_read('h0, 'h1034);
    cpuif.assert_read('h2, 'h0000);
    cpuif.assert_read('h4, 'h9A10);
    cpuif.assert_read('h6, 'h0000);

    // rw_reg2
    assert(cb.hwif_out.rw_reg2.f1.value == 0);
    assert(cb.hwif_out.rw_reg2.f2.value == 0);
    cpuif.write('h8, 'h1234);
    cpuif.write('hA, 'h5678);
    cpuif.write('hC, 'h9ABC);
    cpuif.write('hE, 'hDEF1);
    @cb;
    assert(cb.hwif_out.rw_reg2.f1.value == 4'h8);
    assert(cb.hwif_out.rw_reg2.f2.value == 16'hDEF1);
    cpuif.assert_read('h8, 'h0000);
    cpuif.assert_read('hA, 'h0008);
    cpuif.assert_read('hC, 'h0000);
    cpuif.assert_read('hE, 'hDEF1);

    // rw_reg1_lsb0
    assert(cb.hwif_out.rw_reg1_lsb0.f1.value == 0);
    assert(cb.hwif_out.rw_reg1_lsb0.f2.value == 0);
    assert(cb.hwif_out.rw_reg1_lsb0.f3.value == 0);
    assert(cb.hwif_out.rw_reg1_lsb0.f4.value == 0);
    cpuif.write('h10, 'h1234);
    cpuif.write('h12, 'h5678);
    cpuif.write('h14, 'h9ABC);
    cpuif.write('h16, 'hDEF1);
    @cb;
    assert(`bitswap(cb.hwif_out.rw_reg1_lsb0.f1.value) == 8'h34);
    assert(`bitswap(cb.hwif_out.rw_reg1_lsb0.f2.value) == 3'h1);
    assert(`bitswap(cb.hwif_out.rw_reg1_lsb0.f3.value) == 1'h1);
    assert(`bitswap(cb.hwif_out.rw_reg1_lsb0.f4.value) == 8'h9A);
    cpuif.assert_read('h10, 'h1034);
    cpuif.assert_read('h12, 'h0000);
    cpuif.assert_read('h14, 'h9A10);
    cpuif.assert_read('h16, 'h0000);

    // rw_reg2_lsb0
    assert(cb.hwif_out.rw_reg2_lsb0.f1.value == 0);
    assert(cb.hwif_out.rw_reg2_lsb0.f2.value == 0);
    cpuif.write('h18, 'h1234);
    cpuif.write('h1A, 'h5678);
    cpuif.write('h1C, 'h9ABC);
    cpuif.write('h1E, 'hDEF1);
    @cb;
    assert(`bitswap(cb.hwif_out.rw_reg2_lsb0.f1.value) == 4'h8);
    assert(`bitswap(cb.hwif_out.rw_reg2_lsb0.f2.value) == 16'hDEF1);
    cpuif.assert_read('h18, 'h0000);
    cpuif.assert_read('h1A, 'h0008);
    cpuif.assert_read('h1C, 'h0000);
    cpuif.assert_read('h1E, 'hDEF1);

    // r_reg
    cpuif.assert_read('h20, 0);
    cpuif.assert_read('h22, 0);
    cb.hwif_in.r_reg.f1.next <= 8'hAB;
    cb.hwif_in.r_reg.f2.next <= 11'h4DE;
    @cb;
    cpuif.assert_read('h20, 'hB000);
    cpuif.assert_read('h22, 'h4DEA);

    // r_reg_lsb0
    cpuif.assert_read('h24, 0);
    cpuif.assert_read('h26, 0);
    cb.hwif_in.r_reg_lsb0.f1.next <= {<<{8'hAB}};
    cb.hwif_in.r_reg_lsb0.f2.next <= {<<{11'h4DE}};
    @cb;
    cpuif.assert_read('h24, 'hB000);
    cpuif.assert_read('h26, 'h4DEA);

    // r_reg2
    cpuif.assert_read('h28, 0);
    cpuif.assert_read('h2a, 0);
    cpuif.assert_read('h2c, 0);
    cpuif.assert_read('h2e, 0);
    cb.hwif_in.r_reg2.f1.next <= 20'hABCDE;
    cb.hwif_in.r_reg2.f2.next <= 2'h3;
    @cb;
    cpuif.assert_read('h28, 'hE000);
    cpuif.assert_read('h2a, 'hABCD);
    cpuif.assert_read('h2c, 'h0000);
    cpuif.assert_read('h2e, 'h0003);

    // counter_reg
    cpuif.assert_read('h30, 16'h0204);

    // r_reg3
    cpuif.assert_read('h34, 16'h5678);
    cpuif.assert_read('h36, 16'h1234);
    assert(cb.hwif_out.r_reg3.f1.value == 32'h12345678);

    // r_reg4
    cpuif.assert_read('h38, 16'h2C48);
    cpuif.assert_read('h3A, 16'h1E6A);
    assert(cb.hwif_out.r_reg4.f1.value == 32'h12345678);

{% endblock %}
