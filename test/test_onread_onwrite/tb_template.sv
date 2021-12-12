{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    cpuif.assert_read('h0, 'h0F_F0);
    cpuif.assert_read('h0, 'hFF_00);
    cpuif.write      ('h0, 'h00_FF);
    cpuif.assert_read('h0, 'h00_FF);
    cpuif.assert_read('h0, 'hFF_00);

    cpuif.assert_read('h4, 'h0_F_0);
    cpuif.write      ('h4, 'h1_1_1);
    cpuif.assert_read('h4, 'h1_E_1);
    cpuif.write      ('h4, 'h1_2_2);
    cpuif.assert_read('h4, 'h0_C_3);

    cpuif.assert_read('h8, 'h0_F_0);
    cpuif.write      ('h8, 'hE_E_E);
    cpuif.assert_read('h8, 'h1_E_1);
    cpuif.write      ('h8, 'hE_D_D);
    cpuif.assert_read('h8, 'h0_C_3);

    cpuif.assert_read('hC, 'h0F_F0);
    cpuif.write      ('hC, 'h12_34);
    cpuif.assert_read('hC, 'hFF_00);
{% endblock %}
