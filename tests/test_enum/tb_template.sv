{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // check initial conditions
    cpuif.assert_read('h0, regblock_pkg::top__my_enum_e__val_2);
    cpuif.assert_read('h0, 'h4');

    //---------------------------------
    // set r0 = val_1
    cpuif.write('h0, regblock_pkg::top__my_enum_e__val_1);

    cpuif.assert_read('h0, regblock_pkg::top__my_enum_e__val_1);
    cpuif.assert_read('h0, 'h0');

{% endblock %}
