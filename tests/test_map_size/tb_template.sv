{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    // check block size
    assert(regblock_pkg::REGBLOCK_SIZE == {{exporter.ds.top_node.size}});

{% endblock %}
