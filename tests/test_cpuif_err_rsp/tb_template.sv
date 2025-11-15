{% extends "lib/tb_base.sv" %}

{%- block dut_support %}
    {% sv_line_anchor %}

    external_block #(
        .ADDR_WIDTH(3)
    ) mem_rw_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mem_rw.req),
        .req_is_wr(hwif_out.mem_rw.req_is_wr),
        .addr(hwif_out.mem_rw.addr),
        .wr_data(hwif_out.mem_rw.wr_data),
        .wr_biten(hwif_out.mem_rw.wr_biten),
        .rd_ack(hwif_in.mem_rw.rd_ack),
        .rd_data(hwif_in.mem_rw.rd_data),
        .wr_ack(hwif_in.mem_rw.wr_ack)
    );

    external_block #(
        .ADDR_WIDTH(3)
    ) mem_ro_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mem_ro.req),
        .req_is_wr(hwif_out.mem_ro.req_is_wr),
        .addr(hwif_out.mem_ro.addr),
        .wr_data(32'b0),
        .wr_biten(32'b0),
        .rd_ack(hwif_in.mem_ro.rd_ack),
        .rd_data(hwif_in.mem_ro.rd_data),
        .wr_ack(hwif_in.mem_ro.wr_ack)
    );

    external_block #(
        .ADDR_WIDTH(3)
    ) mem_wo_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mem_wo.req),
        .req_is_wr(hwif_out.mem_wo.req_is_wr),
        .addr(hwif_out.mem_wo.addr),
        .wr_data(hwif_out.mem_wo.wr_data),
        .wr_biten(hwif_out.mem_wo.wr_biten),
        .rd_ack(),
        .rd_data(),
        .wr_ack(hwif_in.mem_wo.wr_ack)
    );
    assign hwif_in.mem_wo.rd_ack = '0;
    assign hwif_in.mem_wo.rd_data = '0;

    external_block #(
        .ADDR_WIDTH(4)
    ) external_rf_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.external_rf.req),
        .req_is_wr(hwif_out.external_rf.req_is_wr),
        .addr(hwif_out.external_rf.addr),
        .wr_data(hwif_out.external_rf.wr_data),
        .wr_biten(hwif_out.external_rf.wr_biten),
        .rd_ack(hwif_in.external_rf.rd_ack),
        .rd_data(hwif_in.external_rf.rd_data),
        .wr_ack(hwif_in.external_rf.wr_ack)
    );

{%- endblock %}

{% block seq %}

logic wr_err;
logic expected_wr_err;
logic expected_rd_err;
logic bad_addr_expected_err;
logic bad_rw_expected_wr_err;
logic bad_rw_expected_rd_err;
logic [7:0] addr;

    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

{%- if testcase.err_if_bad_addr %}
        bad_addr_expected_err = 1'b1;
{%- else %}
        bad_addr_expected_err = 1'b0;
{%- endif %}

{%- if testcase.err_if_bad_rw %}
        bad_rw_expected_wr_err = 1'b1;
        bad_rw_expected_rd_err = 1'b1;
{%- else %}
        bad_rw_expected_wr_err = 1'b0;
        bad_rw_expected_rd_err = 1'b0;
{%- endif %}

    // r_rw - sw=rw; hw=na; // Storage element
    addr = 'h0;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    cpuif.assert_read(addr, 40, .expects_err(expected_rd_err));
    cpuif.write('h0, 61, .expects_err(expected_wr_err));
    cpuif.assert_read('h0, 61, .expects_err(expected_rd_err));

    // r_r - sw=r; hw=na; // Wire/Bus - constant value
    addr = 'h4;
    expected_rd_err = 'h0;
    expected_wr_err = bad_rw_expected_wr_err;
    cpuif.assert_read(addr, 80, .expects_err(expected_rd_err));
    cpuif.write(addr, 81, .expects_err(expected_wr_err));
    cpuif.assert_read(addr, 80, .expects_err(expected_rd_err));

    // r_wo - sw=w; hw=r; // Storage element
    addr = 'h8;
    expected_rd_err = bad_rw_expected_rd_err;
    expected_wr_err = 'h0;
    cpuif.assert_read(addr, 0, .expects_err(expected_rd_err));
    assert(cb.hwif_out.r_wo.f.value == 100);

    cpuif.write(addr, 101, .expects_err(expected_wr_err));
    cpuif.assert_read(addr, 0, .expects_err(expected_rd_err));
    assert(cb.hwif_out.r_wo.f.value == 101);

    // Reading/writing from/to non existing register
    addr = 'h18;
    cpuif.assert_read(addr, 0, .expects_err(bad_addr_expected_err));
    cpuif.write(addr, 'h8C, .expects_err(bad_addr_expected_err));

    // Reading/writing from/to combined read AND write only register
    addr = 'h1C;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    cpuif.assert_read(addr, 200, .expects_err(expected_rd_err));
    cpuif.write(addr, 'h8C, .expects_err(expected_wr_err));

    // External memories
    // mem_rw - sw=rw;
    addr = 'h20;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    mem_rw_inst.mem[0] = 'h8C;
    cpuif.assert_read(addr, 'h8C, .expects_err(expected_rd_err));
    cpuif.write(addr, 'h8D, .expects_err(expected_wr_err));
    cpuif.assert_read(addr, 'h8D, .expects_err(expected_rd_err));

    // mem_r - sw=r;
    addr = 'h28;
    expected_rd_err = 'h0;
    expected_wr_err = bad_rw_expected_wr_err;
    mem_ro_inst.mem[0] = 'hB4;
    cpuif.assert_read(addr, 'hB4, .expects_err(expected_rd_err));
    cpuif.write(addr, 'hB5, .expects_err(expected_wr_err));
    cpuif.assert_read(addr, 'hB4, .expects_err(expected_rd_err));


    // mem_w - sw=w;
    addr = 'h30;
    expected_rd_err = bad_rw_expected_rd_err;
    expected_wr_err = 'h0;
    mem_wo_inst.mem[0] = 'hC8;
    cpuif.assert_read(addr, 0, .expects_err(expected_rd_err));
    assert(mem_wo_inst.mem[0] == 'hC8);

    cpuif.write(addr, 'hC9, .expects_err(expected_wr_err));
    cpuif.assert_read(addr, 0, .expects_err(expected_rd_err));
    assert(mem_wo_inst.mem[0] == 'hC9);

    // External rf;
    addr = 'h40;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    cpuif.assert_read(addr, 'h0, .expects_err(expected_rd_err));
    cpuif.write(addr, 'hD0, .expects_err(expected_wr_err));
    cpuif.assert_read(addr, 'hD0, .expects_err(expected_rd_err));
{% endblock %}
