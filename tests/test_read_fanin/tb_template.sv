{% extends "lib/tb_base.sv" %}

{%- block declarations %}
    {% sv_line_anchor %}
    localparam REGWIDTH = {{testcase.regwidth}};
    localparam STRIDE = REGWIDTH/8;
    localparam N_REGS = {{testcase.n_regs}};
{%- endblock %}


{% block seq %}
    {% sv_line_anchor %}
    bit [REGWIDTH-1:0] data[N_REGS];

    ##1;
    cb.rst <= '0;
    ##1;

    foreach(data[i]) data[i] = {$urandom(), $urandom(), $urandom(), $urandom()};

    for(int i=0; i<N_REGS; i++) begin
        cpuif.assert_read(i*STRIDE, 'h1);
    end

    for(int i=0; i<N_REGS; i++) begin
        cpuif.write(i*STRIDE, data[i]);
    end

    for(int i=0; i<N_REGS; i++) begin
        cpuif.assert_read(i*STRIDE, data[i]);
    end

    assert($bits(dut.cpuif_wr_data) == REGWIDTH);
{% endblock %}
