{% extends "lib/tb_base.sv" %}



{%- block dut_support %}
    {% sv_line_anchor %}

    external_reg_err ext_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.ext_reg.req),
        .req_is_wr(hwif_out.ext_reg.req_is_wr),
        .wr_data(hwif_out.ext_reg.wr_data),
        .wr_biten(hwif_out.ext_reg.wr_biten),
        .rd_ack(hwif_in.ext_reg.rd_ack),
        .rd_data(hwif_in.ext_reg.rd_data),
        .rd_err(hwif_in.ext_reg.rd_err),
        .wr_ack(hwif_in.ext_reg.wr_ack),
        .wr_err(hwif_in.ext_reg.wr_err)
    );

    external_reg_err #(
        .SUBWORDS(2)
    ) wide_ext_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.wide_ext_reg.req),
        .req_is_wr(hwif_out.wide_ext_reg.req_is_wr),
        .wr_data(hwif_out.wide_ext_reg.wr_data),
        .wr_biten(hwif_out.wide_ext_reg.wr_biten),
        .rd_ack(hwif_in.wide_ext_reg.rd_ack),
        .rd_data(hwif_in.wide_ext_reg.rd_data),
        .rd_err(hwif_in.wide_ext_reg.rd_err),
        .wr_ack(hwif_in.wide_ext_reg.wr_ack),
        .wr_err(hwif_in.wide_ext_reg.wr_err)
    );

    for(genvar i=0; i<32; i++) begin : array
        external_reg_err ext_reg_inst (
            .clk(clk),
            .rst(rst),

            .req(hwif_out.ext_reg_array[i].req),
            .req_is_wr(hwif_out.ext_reg_array[i].req_is_wr),
            .wr_data(hwif_out.ext_reg_array[i].wr_data),
            .wr_biten(hwif_out.ext_reg_array[i].wr_biten),
            .rd_ack(hwif_in.ext_reg_array[i].rd_ack),
            .rd_data(hwif_in.ext_reg_array[i].rd_data),
            .rd_err(hwif_in.ext_reg_array[i].rd_err),
            .wr_ack(hwif_in.ext_reg_array[i].wr_ack),
            .wr_err(hwif_in.ext_reg_array[i].wr_err)
        );
    end

    external_block_err #(
        .ADDR_WIDTH(5)
    ) rf_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.rf.req),
        .req_is_wr(hwif_out.rf.req_is_wr),
        .addr(hwif_out.rf.addr),
        .wr_data(hwif_out.rf.wr_data),
        .wr_biten(hwif_out.rf.wr_biten),
        .rd_ack(hwif_in.rf.rd_ack),
        .rd_data(hwif_in.rf.rd_data),
        .rd_err(hwif_in.rf.rd_err),
        .wr_ack(hwif_in.rf.wr_ack),
        .wr_err(hwif_in.rf.wr_err)
    );

    external_block_err #(
        .ADDR_WIDTH(5)
    ) am_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.am.req),
        .req_is_wr(hwif_out.am.req_is_wr),
        .addr(hwif_out.am.addr),
        .wr_data(hwif_out.am.wr_data),
        .wr_biten(hwif_out.am.wr_biten),
        .rd_ack(hwif_in.am.rd_ack),
        .rd_data(hwif_in.am.rd_data),
        .rd_err(hwif_in.am.rd_err),
        .wr_ack(hwif_in.am.wr_ack),
        .wr_err(hwif_in.am.wr_err)
    );

    external_block_err #(
        .ADDR_WIDTH(5)
    ) mm_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mm.req),
        .req_is_wr(hwif_out.mm.req_is_wr),
        .addr(hwif_out.mm.addr),
        .wr_data(hwif_out.mm.wr_data),
        .wr_biten(hwif_out.mm.wr_biten),
        .rd_ack(hwif_in.mm.rd_ack),
        .rd_data(hwif_in.mm.rd_data),
        .rd_err(hwif_in.mm.rd_err),
        .wr_ack(hwif_in.mm.wr_ack),
        .wr_err(hwif_in.mm.wr_err)
    );

    external_reg_err wo_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.wo_reg.req),
        .req_is_wr(hwif_out.wo_reg.req_is_wr),
        .wr_data(hwif_out.wo_reg.wr_data),
        .wr_biten(hwif_out.wo_reg.wr_biten),
        .rd_ack(),
        .rd_data(),
        .wr_ack(hwif_in.wo_reg.wr_ack),
        .wr_err(hwif_in.wo_reg.wr_err)
    );

    external_reg_err ro_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.ro_reg.req),
        .req_is_wr(hwif_out.ro_reg.req_is_wr),
        .wr_data(32'b0),
        .wr_biten(32'b0),
        .rd_ack(hwif_in.ro_reg.rd_ack),
        .rd_data(hwif_in.ro_reg.rd_data),
        .rd_err(hwif_in.ro_reg.rd_err),
        .wr_ack(),
        .wr_err()
    );

    external_reg_err #(
        .SUBWORDS(2)
    ) wide_wo_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.wide_wo_reg.req),
        .req_is_wr(hwif_out.wide_wo_reg.req_is_wr),
        .wr_data(hwif_out.wide_wo_reg.wr_data),
        .wr_biten(hwif_out.wide_wo_reg.wr_biten),
        .rd_ack(),
        .rd_data(),
        .wr_ack(hwif_in.wide_wo_reg.wr_ack),
        .wr_err(hwif_in.wide_wo_reg.wr_err)
    );

    external_reg_err #(
        .SUBWORDS(2)
    ) wide_ro_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.wide_ro_reg.req),
        .req_is_wr(hwif_out.wide_ro_reg.req_is_wr),
        .wr_data(32'b0),
        .wr_biten(32'b0),
        .rd_ack(hwif_in.wide_ro_reg.rd_ack),
        .rd_data(hwif_in.wide_ro_reg.rd_data),
        .rd_err(hwif_in.wide_ro_reg.rd_err),
        .wr_ack(),
        .wr_err()
    );
{%- endblock %}



{% block seq %}
    logic [31:0] x;
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Error read/write tests
    //--------------------------------------------------------------------------

    // External register with r/w/rw fields
    cpuif.write('h00, '0, .expects_err(1'b1));
    cpuif.assert_read('h00, '0, .expects_err(1'b1));

    for(int i=0; i<2; i++) begin
        // External wide register with rw field
        cpuif.write('h10 + i*4, '0, .expects_err(1'b1));
        cpuif.assert_read('h10 + i*4, '0, .expects_err(1'b1));
    end

    for(int i=0; i<32; i++) begin
        // External register array with rw fields
        cpuif.write('h100 + i*4, '0, .expects_err(1'b1));
        cpuif.assert_read('h100 + i*4, '0, .expects_err(1'b1));
    end

    for(int i=0; i<8; i++) begin
        // External register file with rw fields
        cpuif.write('h1000 + i*4, '0, .expects_err(1'b1));
        cpuif.assert_read('h1000 + i*4, '0, .expects_err(1'b1));
    end

    for(int i=0; i<8; i++) begin
        // Address map -> always external with rw
        cpuif.write('h2000 + i*4, '0, .expects_err(1'b1));
        cpuif.assert_read('h2000 + i*4, '0, .expects_err(1'b1));
    end

    for(int i=0; i<8; i++) begin
        // External memory with rw fields
        cpuif.write('h3000 + i*4, '0, .expects_err(1'b1));
        cpuif.assert_read('h3000 + i*4, '0, .expects_err(1'b1));
    end

    // External RO register
    cpuif.write('h4000, '1);
    cpuif.assert_read('h4000, '0, .expects_err(1'b1));

    // External WO register
    cpuif.write('h4004, '1, .expects_err(1'b1));
    cpuif.assert_read('h4004, '0);

    for(int i=0; i<2; i++) begin
        // External wide RO register
        cpuif.write('h4010 + i*4, '1);
        cpuif.assert_read('h4010 + i*4, '0, .expects_err(1'b1));
    end

    for(int i=0; i<2; i++) begin
        // External wide WO register
        cpuif.write('h4018 + i*4, '1, .expects_err(1'b1));
        cpuif.assert_read('h4018 + i*4, 0);
    end

{% endblock %}
