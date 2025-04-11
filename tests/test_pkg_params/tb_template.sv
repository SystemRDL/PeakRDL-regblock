{% extends "lib/tb_base.sv" %}

{% block seq %}
    {% sv_line_anchor %}
    assert(regblock_pkg::N_REGS == {{testcase.n_regs}});
    assert(regblock_pkg::REGWIDTH == {{testcase.regwidth}});
    assert(regblock_pkg::NAME == "{{testcase.name}}");
{% endblock %}
