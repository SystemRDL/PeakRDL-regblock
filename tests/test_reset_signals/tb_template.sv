{% extends "lib/tb_base.sv" %}

{%- block declarations %}
    logic root_cpuif_reset;
    logic [15:0] r5f2_resetvalue;
{%- endblock %}

{%- block clocking_dirs %}
    output root_cpuif_reset;
    output r5f2_resetvalue;
{%- endblock %}

{% block seq %}
    {% sv_line_anchor %}
    cb.root_cpuif_reset <= '1;
    cb.hwif_in.r2.my_reset <= '1;
    cb.hwif_in.r3.my_areset <= '1;
    cb.hwif_in.r4.my_reset_n <= '0;
    cb.hwif_in.r5.my_areset_n <= '0;
    cb.hwif_in.f2_reset <= '1;
    cb.r5f2_resetvalue <= 'hABCD;
    ##2;
    cb.rst <= '0;
    cb.root_cpuif_reset <= '0;
    cb.hwif_in.r2.my_reset <= '0;
    cb.hwif_in.r3.my_areset <= '0;
    cb.hwif_in.r4.my_reset_n <= '1;
    cb.hwif_in.r5.my_areset_n <= '1;
    cb.hwif_in.f2_reset <= '0;
    ##1;


    cpuif.assert_read('h00, 'h5678_1234);
    cpuif.assert_read('h04, 'h5678_1234);
    cpuif.assert_read('h08, 'h5678_1234);
    cpuif.assert_read('h0c, 'h5678_1234);
    cpuif.assert_read('h10, 'hABCD_1234);

    for(int i=0; i<5; i++) cpuif.write(i*4, 0);

    cpuif.assert_read('h00, 'h0000_0000);
    cpuif.assert_read('h04, 'h0000_0000);
    cpuif.assert_read('h08, 'h0000_0000);
    cpuif.assert_read('h0c, 'h0000_0000);
    cpuif.assert_read('h10, 'h0000_0000);

    cb.rst <= '1;
    @cb;
    cb.rst <= '0;
    @cb;

    cpuif.assert_read('h00, 'h0000_1234);
    cpuif.assert_read('h04, 'h0000_0000);
    cpuif.assert_read('h08, 'h0000_0000);
    cpuif.assert_read('h0c, 'h0000_0000);
    cpuif.assert_read('h10, 'h0000_0000);

    for(int i=0; i<5; i++) cpuif.write(i*4, 0);

    cb.hwif_in.r2.my_reset <= '1;
    @cb;
    cb.hwif_in.r2.my_reset <= '0;
    @cb;

    cpuif.assert_read('h00, 'h0000_0000);
    cpuif.assert_read('h04, 'h0000_1234);
    cpuif.assert_read('h08, 'h0000_0000);
    cpuif.assert_read('h0c, 'h0000_0000);
    cpuif.assert_read('h10, 'h0000_0000);

    for(int i=0; i<5; i++) cpuif.write(i*4, 0);

    ##1;
    #2ns;
    hwif_in.r3.my_areset = '1;
    #1ns;
    hwif_in.r3.my_areset = '0;
    ##1;

    cpuif.assert_read('h00, 'h0000_0000);
    cpuif.assert_read('h04, 'h0000_0000);
    cpuif.assert_read('h08, 'h0000_1234);
    cpuif.assert_read('h0c, 'h0000_0000);
    cpuif.assert_read('h10, 'h0000_0000);

    for(int i=0; i<5; i++) cpuif.write(i*4, 0);

    cb.hwif_in.r4.my_reset_n <= '0;
    @cb;
    cb.hwif_in.r4.my_reset_n <= '1;
    @cb;

    cpuif.assert_read('h00, 'h0000_0000);
    cpuif.assert_read('h04, 'h0000_0000);
    cpuif.assert_read('h08, 'h0000_0000);
    cpuif.assert_read('h0c, 'h0000_1234);
    cpuif.assert_read('h10, 'h0000_0000);

    for(int i=0; i<5; i++) cpuif.write(i*4, 0);

    ##1;
    #2ns;
    hwif_in.r5.my_areset_n = '0;
    #1ns;
    hwif_in.r5.my_areset_n = '1;
    ##1;

    cpuif.assert_read('h00, 'h0000_0000);
    cpuif.assert_read('h04, 'h0000_0000);
    cpuif.assert_read('h08, 'h0000_0000);
    cpuif.assert_read('h0c, 'h0000_0000);
    cpuif.assert_read('h10, 'h0000_1234);

    for(int i=0; i<5; i++) cpuif.write(i*4, 0);

    @cb;
    cb.hwif_in.f2_reset <= '1;
    cb.r5f2_resetvalue <= 'h3210;
    @cb;
    cb.hwif_in.f2_reset <= '0;

    cpuif.assert_read('h00, 'h5678_0000);
    cpuif.assert_read('h04, 'h5678_0000);
    cpuif.assert_read('h08, 'h5678_0000);
    cpuif.assert_read('h0c, 'h5678_0000);
    cpuif.assert_read('h10, 'h3210_0000);

{% endblock %}
