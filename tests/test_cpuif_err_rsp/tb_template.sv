{% extends "lib/tb_base.sv" %}

{%- block dut_support %}
    {% sv_line_anchor %}

    external_reg ext_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.er_rw.req),
        .req_is_wr(hwif_out.er_rw.req_is_wr),
        .wr_data(hwif_out.er_rw.wr_data),
        .wr_biten(hwif_out.er_rw.wr_biten),
        .rd_ack(hwif_in.er_rw.rd_ack),
        .rd_data(hwif_in.er_rw.rd_data),
        .wr_ack(hwif_in.er_rw.wr_ack)
    );

    external_reg ro_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.er_r.req),
        .req_is_wr(hwif_out.er_r.req_is_wr),
        .wr_data(32'b0),
        .wr_biten(32'b0),
        .rd_ack(hwif_in.er_r.rd_ack),
        .rd_data(hwif_in.er_r.rd_data),
        .wr_ack()
    );

    external_reg wo_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.er_w.req),
        .req_is_wr(hwif_out.er_w.req_is_wr),
        .wr_data(hwif_out.er_w.wr_data),
        .wr_biten(hwif_out.er_w.wr_biten),
        .rd_ack(),
        .rd_data(),
        .wr_ack(hwif_in.er_w.wr_ack)
    );

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

        .req(hwif_out.mem_r.req),
        .req_is_wr(hwif_out.mem_r.req_is_wr),
        .addr(hwif_out.mem_r.addr),
        .wr_data(32'b0),
        .wr_biten(32'b0),
        .rd_ack(hwif_in.mem_r.rd_ack),
        .rd_data(hwif_in.mem_r.rd_data),
        .wr_ack(hwif_in.mem_r.wr_ack)
    );

        external_block #(
        .ADDR_WIDTH(3)
    ) mem_wo_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mem_w.req),
        .req_is_wr(hwif_out.mem_w.req_is_wr),
        .addr(hwif_out.mem_w.addr),
        .wr_data(hwif_out.mem_w.wr_data),
        .wr_biten(hwif_out.mem_w.wr_biten),
        .rd_ack(),
        .rd_data(),
        .wr_ack(hwif_in.mem_w.wr_ack)
    );

{%- endblock %}

{% block seq %}

logic wr_err;
logic expected_wr_err;
logic expected_rd_err;
logic [5:0] addr;

    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;



    // r_rw - sw=rw; hw=na; // Storage element
    addr = 'h0;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    cpuif.assert_read_err(addr, 40, expected_rd_err);
    cpuif.assert_write_err('h0, 41, expected_wr_err, '1);
    cpuif.assert_read_err('h0, 41, expected_rd_err);

    // r_r - sw=r; hw=na; // Wire/Bus - constant value
    addr = 'h4;
    expected_rd_err = 'h0;
    expected_wr_err = 'h1;
    cpuif.assert_read_err(addr, 80,expected_rd_err);
    cpuif.assert_write_err(addr, 81, expected_wr_err, '1);
    cpuif.assert_read_err(addr, 80, expected_rd_err);

    // r_w - sw=w; hw=r; // Storage element
    addr = 'h8;
    expected_rd_err = 'h1;
    expected_wr_err = 'h0;
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(cb.hwif_out.r_w.f.value == 100);

    cpuif.assert_write_err(addr, 101, expected_wr_err, '1);
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(cb.hwif_out.r_w.f.value == 101);

    // External registers
    // er_rw - sw=rw; hw=na; // Storage element
    addr = 'hC;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    ext_reg_inst.value = 'h8C;
    cpuif.assert_read_err(addr, 140, expected_rd_err);
    cpuif.assert_write_err('h0, 141, expected_wr_err);
    cpuif.assert_read_err('h0, 141, expected_rd_err);

    // er_r - sw=r; hw=na; // Wire/Bus - constant value
    addr = 'h10;
    expected_rd_err = 'h0;
    expected_wr_err = 'h1;
    ro_reg_inst.value = 'hB4;
    cpuif.assert_read_err(addr, 180,expected_rd_err);
    cpuif.assert_write_err(addr, 181, expected_wr_err);
    cpuif.assert_read_err(addr, 180, expected_rd_err);

    // er_w - sw=w; hw=r; // Storage element
    addr = 'h14;
    expected_rd_err = 'h1;
    expected_wr_err = 'h0;
    wo_reg_inst.value = 'hC8;
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(wo_reg_inst.value == 200);

    cpuif.assert_write_err(addr, 201, expected_wr_err);
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(wo_reg_inst.value == 201);

    // Reading/writing from/to non exiting register
    addr = 'h18;
    expected_rd_err = 'h1;
    expected_wr_err = 'h1;
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    cpuif.assert_write_err(addr, 140, expected_wr_err);

    // External memories
    // mem_rw - sw=rw;
    addr = 'h20;
    expected_rd_err = 'h0;
    expected_wr_err = 'h0;
    mem_rw_inst.mem[0] = 'h8C;
    cpuif.assert_read_err(addr, 140, expected_rd_err);
    cpuif.assert_write_err('h0, 141, expected_wr_err);
    cpuif.assert_read_err('h0, 141, expected_rd_err);

    // mem_r - sw=r;
    addr = 'h28;
    expected_rd_err = 'h0;
    expected_wr_err = 'h1;
    mem_ro_inst.mem[0] = 'hB4;
    cpuif.assert_read_err(addr, 180,expected_rd_err);
    cpuif.assert_write_err(addr, 181, expected_wr_err);
    cpuif.assert_read_err(addr, 180, expected_rd_err);


    // mem_w - sw=w;
    addr = 'h30;
    expected_rd_err = 'h1;
    expected_wr_err = 'h0;
    mem_wo_inst.mem[0] = 'hC8;
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(mem_wo_inst.mem[0] == 200);

    cpuif.assert_write_err(addr, 201, expected_wr_err);
    cpuif.assert_read_err(addr, 0, expected_rd_err);
    assert(mem_wo_inst.mem[0] == 201);

{% endblock %}
