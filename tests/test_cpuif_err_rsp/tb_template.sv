{% extends "lib/tb_base.sv" %}

{% block seq %}

logic wr_err;
logic expected_wr_err;
logic expected_rd_err;
logic [3:0] addr;

    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;



    // r_rw - sw=rw; hw=na; // Storage element
    assign addr = 'h0;
    assign expected_rd_err = 'h0;
    assign expected_wr_err = 'h0;
    cpuif.assert_read_err(addr, 40, expected_rd_err);
    cpuif.write_err('h0, 41, '1, wr_err);
    assert(wr_err == expected_wr_err) else $error("Error write response from 0x%x returned 0x%x. Expected 0x%x", addr, wr_err, expected_wr_err);
    cpuif.assert_read_err('h0, 41, expected_rd_err);

    // r_r - sw=r; hw=na; // Wire/Bus - constant value
    assign addr = 'h4;
    assign expected_rd_err = 'h0;
    assign expected_wr_err = 'h1;
    cpuif.assert_read_err(addr, 80,expected_rd_err);
    cpuif.write_err(addr, 81, '1, wr_err);
    assert(wr_err == expected_wr_err) else $error("Error write response from 0x%x returned 0x%x. Expected 0x%x", addr, wr_err, expected_wr_err);
    cpuif.assert_read_err(addr, 80, expected_rd_err);


    // r_w - sw=w; hw=r; // Storage element
    assign addr = 'h8;
    assign expected_rd_err = 'h1;
    assign expected_wr_err = 'h0;
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(cb.hwif_out.r_w.f.value == 100);

    cpuif.write_err(addr, 101, '1, wr_err);
    assert(wr_err == expected_wr_err) else $error("Error write response from 0x%x returned 0x%x. Expected 0x%x", addr, wr_err, expected_wr_err);
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(cb.hwif_out.r_w.f.value == 101);

{% endblock %}
