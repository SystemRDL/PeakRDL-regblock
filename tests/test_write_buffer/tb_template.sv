{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    cb.hwif_in.trigger_sig_n <= '1;
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Wide registers
    //--------------------------------------------------------------------------

    // reg1
    cpuif.assert_read('h0, 'h0);
    cpuif.assert_read('h2, 'h0);
    cpuif.assert_read('h4, 'h0);
    cpuif.assert_read('h6, 'h0);
    assert(cb.hwif_out.reg1.f1.value == 0);
    cpuif.write('h0, 'h1234);
    cpuif.assert_read('h0, 'h0);
    cpuif.assert_read('h2, 'h0);
    cpuif.assert_read('h4, 'h0);
    cpuif.assert_read('h6, 'h0);
    assert(cb.hwif_out.reg1.f1.value == 0);
    cpuif.write('h2, 'h5678);
    cpuif.assert_read('h0, 'h0);
    cpuif.assert_read('h2, 'h0);
    cpuif.assert_read('h4, 'h0);
    cpuif.assert_read('h6, 'h0);
    assert(cb.hwif_out.reg1.f1.value == 0);
    cpuif.write('h4, 'h9ABC);
    cpuif.assert_read('h0, 'h0);
    cpuif.assert_read('h2, 'h0);
    cpuif.assert_read('h4, 'h0);
    cpuif.assert_read('h6, 'h0);
    assert(cb.hwif_out.reg1.f1.value == 0);
    cpuif.write('h6, 'hDEF1);
    @cb; @cb;
    assert(cb.hwif_out.reg1.f1.value == 64'hDEF19ABC56781234);
    cpuif.assert_read('h0, 'h1234);
    cpuif.assert_read('h2, 'h5678);
    cpuif.assert_read('h4, 'h9ABC);
    cpuif.assert_read('h6, 'hDEF1);

    // reg1_msb0
    cpuif.assert_read('h8, 'h0);
    cpuif.assert_read('hA, 'h0);
    cpuif.assert_read('hC, 'h0);
    cpuif.assert_read('hE, 'h0);
    assert(cb.hwif_out.reg1_msb0.f1.value == 0);
    cpuif.write('h8, 'h1234);
    cpuif.assert_read('h8, 'h0);
    cpuif.assert_read('hA, 'h0);
    cpuif.assert_read('hC, 'h0);
    cpuif.assert_read('hE, 'h0);
    assert(cb.hwif_out.reg1_msb0.f1.value == 0);
    cpuif.write('hA, 'h5678);
    cpuif.assert_read('h8, 'h0);
    cpuif.assert_read('hA, 'h0);
    cpuif.assert_read('hC, 'h0);
    cpuif.assert_read('hE, 'h0);
    assert(cb.hwif_out.reg1_msb0.f1.value == 0);
    cpuif.write('hC, 'h9ABC);
    cpuif.assert_read('h8, 'h0);
    cpuif.assert_read('hA, 'h0);
    cpuif.assert_read('hC, 'h0);
    cpuif.assert_read('hE, 'h0);
    assert(cb.hwif_out.reg1_msb0.f1.value == 0);
    cpuif.write('hE, 'hDEF1);
    @cb; @cb;
    assert({<<{cb.hwif_out.reg1_msb0.f1.value}} == 64'hDEF19ABC56781234);
    cpuif.assert_read('h8, 'h1234);
    cpuif.assert_read('hA, 'h5678);
    cpuif.assert_read('hC, 'h9ABC);
    cpuif.assert_read('hE, 'hDEF1);

    // reg2
    cpuif.assert_read('h10, 'h0);
    cpuif.assert_read('h12, 'h0);
    assert(cb.hwif_out.reg2.f1.value == 0);
    assert(cb.hwif_out.reg2.f2.value == 0);
    cpuif.write('h10, 'h34AA);
    cpuif.assert_read('h10, 'h0);
    cpuif.assert_read('h12, 'h0);
    assert(cb.hwif_out.reg2.f1.value == 0);
    assert(cb.hwif_out.reg2.f2.value == 0);
    cpuif.write('h12, 'hAA12);
    @cb; @cb;
    assert(cb.hwif_out.reg2.f1.value == 12'h234);
    assert(cb.hwif_out.reg2.f2.value == 4'h1);
    cpuif.assert_read('h10, 'h3400);
    cpuif.assert_read('h12, 'h0012);

    // reg2_msb0
    cpuif.assert_read('h14, 'h0);
    cpuif.assert_read('h16, 'h0);
    assert(cb.hwif_out.reg2_msb0.f1.value == 0);
    assert(cb.hwif_out.reg2_msb0.f2.value == 0);
    cpuif.write('h14, 'h34AA);
    cpuif.assert_read('h14, 'h0);
    cpuif.assert_read('h16, 'h0);
    assert(cb.hwif_out.reg2_msb0.f1.value == 0);
    assert(cb.hwif_out.reg2_msb0.f2.value == 0);
    cpuif.write('h16, 'hAA12);
    @cb; @cb;
    assert({<<{cb.hwif_out.reg2_msb0.f1.value}} == 12'h234);
    assert({<<{cb.hwif_out.reg2_msb0.f2.value}} == 4'h1);
    cpuif.assert_read('h14, 'h3400);
    cpuif.assert_read('h16, 'h0012);

    //--------------------------------------------------------------------------
    // Alternate Triggers
    //--------------------------------------------------------------------------

    // g1
    cpuif.assert_read('h18, 'h0);
    cpuif.assert_read('h1A, 'h0);
    assert(cb.hwif_out.g1_r1.f1.value == 0);
    assert(cb.hwif_out.g1_r2.f1.value == 0);
    cpuif.write('h1A, 'h1234);
    cpuif.assert_read('h18, 'h0);
    cpuif.assert_read('h1A, 'h0);
    assert(cb.hwif_out.g1_r1.f1.value == 0);
    assert(cb.hwif_out.g1_r2.f1.value == 0);
    cpuif.write('h18, 'hABCD);
    @cb;
    assert(cb.hwif_out.g1_r1.f1.value == 'hABCD);
    assert(cb.hwif_out.g1_r2.f1.value == 'h1234);

    // g2
    cpuif.assert_read('h1C, 'h0);
    cpuif.assert_read('h1E, 'h0);
    assert(cb.hwif_out.g2_r1.f1.value == 0);
    assert(cb.hwif_out.g2_r2.f1.value == 0);
    cpuif.write('h1C, 'h5678);
    cpuif.write('h1E, 'h9876);
    cpuif.assert_read('h1C, 'h0);
    cpuif.assert_read('h1E, 'h0);
    assert(cb.hwif_out.g2_r1.f1.value == 0);
    assert(cb.hwif_out.g2_r2.f1.value == 0);
    cb.hwif_in.trigger_sig <= '1;
    cb.hwif_in.trigger_sig_n <= '0;
    @cb;
    cb.hwif_in.trigger_sig <= '0;
    cb.hwif_in.trigger_sig_n <= '1;
    @cb;
    assert(cb.hwif_out.g2_r1.f1.value == 'h5678);
    assert(cb.hwif_out.g2_r2.f1.value == 'h9876);

    // g3
    cpuif.assert_read('h20, 'h0);
    assert(cb.hwif_out.g3_r1.f1.value == 0);
    cpuif.write('h20, 'hFEDC);
    @cb; @cb;
    assert(cb.hwif_out.g3_r1.f1.value == 0);
    cpuif.assert_read('h20, 'h0);
    cpuif.write('h22, 'h0000);
    @cb; @cb;
    assert(cb.hwif_out.g3_r1.f1.value == 0);
    cpuif.assert_read('h20, 'h0);
    cpuif.write('h22, 'h0001);
    @cb; @cb;
    assert(cb.hwif_out.g3_r1.f1.value == 'hFEDC);
    cpuif.assert_read('h20, 'hFEDC);

    // g4
    cpuif.assert_read('h24, 'h0);
    assert(cb.hwif_out.g4_r1.f1.value == 0);
    cpuif.write('h24, 'hCAFE);
    @cb; @cb;
    assert(cb.hwif_out.g4_r1.f1.value == 0);
    cpuif.assert_read('h24, 'h0);
    cpuif.write('h26, 'h0000);
    @cb; @cb;
    assert(cb.hwif_out.g4_r1.f1.value == 0);
    cpuif.assert_read('h24, 'h0);
    cpuif.write('h26, 'h000E);
    @cb; @cb;
    assert(cb.hwif_out.g4_r1.f1.value == 0);
    cpuif.assert_read('h24, 'h0);
    cpuif.write('h26, 'h000F);
    @cb; @cb;
    assert(cb.hwif_out.g4_r1.f1.value == 'hCAFE);
    cpuif.assert_read('h24, 'hCAFE);

    //--------------------------------------------------------------------------
    // swmod behavior
    //--------------------------------------------------------------------------
    // g5
    cpuif.assert_read('h28, 'h0);
    cpuif.assert_read('h2A, 'h0);
    cpuif.write('h28, 'h1234);
    cpuif.write('h28, 'h5678);
    cpuif.assert_read('h28, 'h0);
    cpuif.assert_read('h2A, 'h0);
    cb.hwif_in.trigger_sig <= '1;
    @cb;
    cb.hwif_in.trigger_sig <= '0;
    cpuif.assert_read('h28, 'h5678);
    cpuif.assert_read('h2A, 'h1);

    // g6
    cpuif.assert_read('h2E, 'h0);
    cpuif.assert_read('h2C, 'h0);
    cpuif.assert_read('h2E, 'h1);
    cpuif.write('h2C, 'h5678);
    cpuif.write('h2C, 'h1234);
    cpuif.assert_read('h2E, 'h1);
    cpuif.assert_read('h2C, 'h0);
    cpuif.assert_read('h2E, 'h2);
    cb.hwif_in.trigger_sig <= '1;
    @cb;
    cb.hwif_in.trigger_sig <= '0;
    cpuif.assert_read('h2E, 'h3);
    cpuif.assert_read('h2C, 'h1234);
    cpuif.assert_read('h2E, 'h4);

    //--------------------------------------------------------------------------
    // strobes
    //--------------------------------------------------------------------------
    // reg1
    // reset field to known state
    cpuif.write('h0, 'h0000);
    cpuif.write('h2, 'h0000);
    cpuif.write('h4, 'h0000);
    cpuif.write('h6, 'h0000);
    @cb;
    cpuif.assert_read('h0, 'h0);
    cpuif.assert_read('h2, 'h0);
    cpuif.assert_read('h4, 'h0);
    cpuif.assert_read('h6, 'h0);
    assert(cb.hwif_out.reg1.f1.value == 0);

    cpuif.write('h0, 'hABCD, 'hF000);
    cpuif.write('h2, 'h1234, 'h0F00);
    cpuif.write('h4, 'h5678, 'h00F0);
    cpuif.write('h6, 'hEF12, 'h000F);
    @cb;
    cpuif.assert_read('h0, 'hA000);
    cpuif.assert_read('h2, 'h0200);
    cpuif.assert_read('h4, 'h0070);
    cpuif.assert_read('h6, 'h0002);
    assert(cb.hwif_out.reg1.f1.value == 'h0002_0070_0200_A000);

    // Check that strobes are cumulative
    cpuif.write('h0, 'h0030, 'h00F0);
    cpuif.write('h2, 'h0070, 'h00F0);
    cpuif.write('h4, 'h000D, 'h000F);
    cpuif.write('h4, 'hA000, 'hF000);
    cpuif.write('h2, 'h0008, 'h000F);
    cpuif.write('h0, 'h0200, 'h0F00);
    cpuif.write('h6, 'hA000, 'hF000);
    cpuif.write('h6, 'h0F00, 'h0F00);
    @cb;
    cpuif.assert_read('h0, 'hA230);
    cpuif.assert_read('h2, 'h0278);
    cpuif.assert_read('h4, 'hA07D);
    cpuif.assert_read('h6, 'hAF02);
    assert(cb.hwif_out.reg1.f1.value == 'hAF02_A07D_0278_A230);

    // reg1_msb0
    // reset field to known state
    cpuif.write('h8, 'h0000);
    cpuif.write('hA, 'h0000);
    cpuif.write('hC, 'h0000);
    cpuif.write('hE, 'h0000);
    @cb;
    cpuif.assert_read('h8, 'h0);
    cpuif.assert_read('hA, 'h0);
    cpuif.assert_read('hC, 'h0);
    cpuif.assert_read('hE, 'h0);
    assert(cb.hwif_out.reg1_msb0.f1.value == 0);

    cpuif.write('h8, 'hABCD, 'hF000);
    cpuif.write('hA, 'h1234, 'h0F00);
    cpuif.write('hC, 'h5678, 'h00F0);
    cpuif.write('hE, 'hEF12, 'h000F);
    @cb;
    cpuif.assert_read('h8, 'hA000);
    cpuif.assert_read('hA, 'h0200);
    cpuif.assert_read('hC, 'h0070);
    cpuif.assert_read('hE, 'h0002);
    assert({<<{cb.hwif_out.reg1_msb0.f1.value}} == 'h0002_0070_0200_A000);

    // Check that strobes are cumulative
    cpuif.write('h8, 'h0030, 'h00F0);
    cpuif.write('hA, 'h0070, 'h00F0);
    cpuif.write('hC, 'h000D, 'h000F);
    cpuif.write('hC, 'hA000, 'hF000);
    cpuif.write('hA, 'h0008, 'h000F);
    cpuif.write('h8, 'h0200, 'h0F00);
    cpuif.write('hE, 'hA000, 'hF000);
    cpuif.write('hE, 'h0F00, 'h0F00);
    @cb;
    cpuif.assert_read('h8, 'hA230);
    cpuif.assert_read('hA, 'h0278);
    cpuif.assert_read('hC, 'hA07D);
    cpuif.assert_read('hE, 'hAF02);
    assert({<<{cb.hwif_out.reg1_msb0.f1.value}} == 'hAF02_A07D_0278_A230);


{% endblock %}
