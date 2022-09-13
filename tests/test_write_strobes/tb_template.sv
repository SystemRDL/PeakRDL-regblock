{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    cpuif.assert_read('h0, 'h0_F_0);
    cpuif.write      ('h0, 'h5_5_5, 'h3_3_3);
    cpuif.assert_read('h0, 'h1_E_1);
    cpuif.write      ('h0, 'h5_A_A, 'h3_3_3);
    cpuif.assert_read('h0, 'h0_C_3);

    cpuif.assert_read('h4, 'h0_F_0);
    cpuif.write      ('h4, 'hA_A_A, 'h3_3_3);
    cpuif.assert_read('h4, 'h1_E_1);
    cpuif.write      ('h4, 'hA_5_5, 'h3_3_3);
    cpuif.assert_read('h4, 'h0_C_3);

    cpuif.assert_read('h8, 'h0F_F0);
    cpuif.write      ('h8, 'h12_34, 'hFF_00);
    cpuif.assert_read('h8, 'hFF_00);

    cpuif.assert_read('hC, 'h00);
    cpuif.write      ('hC, 'hFF, 'hF0);
    cpuif.assert_read('hC, 'hF0);
    cpuif.write      ('hC, 'h00, 'h3C);
    cpuif.assert_read('hC, 'hC0);

{% endblock %}
