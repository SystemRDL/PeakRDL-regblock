{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // check initial conditions
    cpuif.assert_read('h4, 'h11);
    cpuif.assert_read('h8, 'h22);
    cpuif.assert_read('hC, 'h33);

    //---------------------------------
    // set hwenable = F0
    cpuif.write('h0, 'h00_F0);

    // test hwenable + we
    cb.hwif_in.r1.f.next <= 'hAB;
    cb.hwif_in.r1.f.we <= '1;
    @cb;
    cb.hwif_in.r1.f.we <= '0;
    cpuif.assert_read('h4, 'hA1);

    // test hwenable + hwclr
    cb.hwif_in.r1.f.hwclr <= '1;
    @cb;
    cb.hwif_in.r1.f.hwclr <= '0;
    cpuif.assert_read('h4, 'h01);

    // test hwenable + hwset
    cb.hwif_in.r1.f.hwset <= '1;
    @cb;
    cb.hwif_in.r1.f.hwset <= '0;
    cpuif.assert_read('h4, 'hF1);


    //---------------------------------
    // set hwmask = F0
    cpuif.write('h0, 'hF0_00);

    // test hwmask + we
    cb.hwif_in.r2.f.next <= 'hAB;
    cb.hwif_in.r2.f.we <= '1;
    @cb;
    cb.hwif_in.r2.f.we <= '0;
    cpuif.assert_read('h8, 'h2B);

    // test hwmask + hwclr
    cb.hwif_in.r2.f.hwclr <= '1;
    @cb;
    cb.hwif_in.r2.f.hwclr <= '0;
    cpuif.assert_read('h8, 'h20);

    // test hwmask + hwset
    cb.hwif_in.r2.f.hwset <= '1;
    @cb;
    cb.hwif_in.r2.f.hwset <= '0;
    cpuif.assert_read('h8, 'h2F);

    //---------------------------------
    // test hwenable + hwclr via reference
    // toggle hwenable = F0, hwclr=1
    cpuif.write('h0, 'h1_00_F0);
    cpuif.write('h0, 'h0_00_00);
    cpuif.assert_read('hC, 'h03);

    // test hwenable + hwset via reference
    // toggle hwenable = 0F, hwset=1
    cpuif.write('h0, 'h2_00_0F);
    cpuif.write('h0, 'h0_00_00);
    cpuif.assert_read('hC, 'h0F);

    // test hwenable + we via reference
    cb.hwif_in.r3.f.next <= 'hAA;
    // toggle hwenable = 0F, we=1
    cpuif.write('h0, 'h4_00_0F);
    cpuif.write('h0, 'h0_00_00);
    cpuif.assert_read('hC, 'h0A);

    //---------------------------------
    // test wel via reference
    cb.hwif_in.r4.f.next <= 'hBB;
    // toggle wel
    cpuif.write('h0, 'h10_00_00);
    cpuif.write('h0, 'h00_00_00);
    cpuif.assert_read('h10, 'hBB);

    cb.hwif_in.r4.f.next <= 'hCC;
    // toggle wel
    cpuif.write('h0, 'h10_00_00);
    cpuif.write('h0, 'h00_00_00);
    cpuif.assert_read('h10, 'hCC);

    //---------------------------------
    // test we and next via reference
    cb.hwif_in.r5.f_next_value <= 'h54;
    cpuif.assert_read('h14, 'h55);
    cb.hwif_in.r5.f_next_value <= 'h56;
    cb.hwif_in.r5.f_we <= '1;
    @cb;
    cb.hwif_in.r5.f_next_value <= '0;
    cb.hwif_in.r5.f_we <= '0;
    cpuif.assert_read('h14, 'h56);
{% endblock %}
