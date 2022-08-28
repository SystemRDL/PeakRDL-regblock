{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // check initial conditions
    cpuif.assert_read('h0, top_my_enum_val_2);

    //---------------------------------
    // set r0 = val_1
    cpuif.write('h0, top_my_enum_val_1);

    cpuif.assert_read('h0, top_my_enum_val_1);

{% endblock %}
