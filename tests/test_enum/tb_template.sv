{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // check enum values
    assert(regblock_pkg::top__my_enum__val_1 == 'd3);
    assert(regblock_pkg::top__my_enum__val_2 == 'd4);

    // check initial conditions
    cpuif.assert_read('h0, regblock_pkg::top__my_enum__val_2);

    //---------------------------------
    // set r0 = val_1
    cpuif.write('h0, regblock_pkg::top__my_enum__val_1);

    cpuif.assert_read('h0, regblock_pkg::top__my_enum__val_1);

{% endblock %}
