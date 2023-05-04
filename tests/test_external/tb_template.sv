{% extends "lib/tb_base.sv" %}



{%- block dut_support %}
    {% sv_line_anchor %}

    external_reg ext_reg_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.ext_reg.req),
        .req_is_wr(hwif_out.ext_reg.req_is_wr),
        .wr_data(hwif_out.ext_reg.wr_data),
        .wr_biten(hwif_out.ext_reg.wr_biten),
        .rd_ack(hwif_in.ext_reg.rd_ack),
        .rd_data(hwif_in.ext_reg.rd_data),
        .wr_ack(hwif_in.ext_reg.wr_ack)
    );

    external_reg #(
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
        .wr_ack(hwif_in.wide_ext_reg.wr_ack)
    );

    for(genvar i=0; i<32; i++) begin : array
        external_reg ext_reg_inst (
            .clk(clk),
            .rst(rst),

            .req(hwif_out.ext_reg_array[i].req),
            .req_is_wr(hwif_out.ext_reg_array[i].req_is_wr),
            .wr_data(hwif_out.ext_reg_array[i].wr_data),
            .wr_biten(hwif_out.ext_reg_array[i].wr_biten),
            .rd_ack(hwif_in.ext_reg_array[i].rd_ack),
            .rd_data(hwif_in.ext_reg_array[i].rd_data),
            .wr_ack(hwif_in.ext_reg_array[i].wr_ack)
        );
    end

    external_block #(
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
        .wr_ack(hwif_in.rf.wr_ack)
    );

    external_block #(
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
        .wr_ack(hwif_in.am.wr_ack)
    );

    external_block #(
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
        .wr_ack(hwif_in.mm.wr_ack)
    );
{%- endblock %}



{% block seq %}
    logic [31:0] x;
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Simple read/write tests
    //--------------------------------------------------------------------------

    repeat(20) begin
        x = $urandom();
        cpuif.write('h00, x);
        cpuif.assert_read('h00, x);
        assert(ext_reg_inst.value == x);
    end

    for(int i=0; i<2; i++) begin
        repeat(20) begin
            x = $urandom();
            cpuif.write('h10 + i*4, x);
            cpuif.assert_read('h10 + i*4, x);
            assert(wide_ext_reg_inst.value[i] == x);
        end
    end

    for(int i=0; i<32; i++) begin
        repeat(20) begin
            x = $urandom();
            cpuif.write('h100 + i*4, x);
            cpuif.assert_read('h100 + i*4, x);
        end
    end

    for(int i=0; i<8; i++) begin
        repeat(20) begin
            x = $urandom();
            cpuif.write('h1000 + i*4, x);
            cpuif.assert_read('h1000 + i*4, x);
            assert(rf_inst.mem[i] == x);
        end
    end

    for(int i=0; i<8; i++) begin
        repeat(20) begin
            x = $urandom();
            cpuif.write('h2000 + i*4, x);
            cpuif.assert_read('h2000 + i*4, x);
            assert(am_inst.mem[i] == x);
        end
    end

    for(int i=0; i<8; i++) begin
        repeat(20) begin
            x = $urandom();
            cpuif.write('h3000 + i*4, x);
            cpuif.assert_read('h3000 + i*4, x);
            assert(mm_inst.mem[i] == x);
        end
    end

    //--------------------------------------------------------------------------
    // Pipelined access
    //--------------------------------------------------------------------------
    // init array with unique known value
    cpuif.write('h4, 'h1234);
    for(int i=0; i<32; i++) begin
        cpuif.write('h100 + i*4, 'h100 + i);
    end
    for(int i=0; i<8; i++) begin
        cpuif.write('h1000 + i*4, 'h1000 + i);
        cpuif.write('h2000 + i*4, 'h2000 + i);
        cpuif.write('h3000 + i*4, 'h3000 + i);
    end

    // random pipelined read/writes
    repeat(256) begin
        fork
            begin
                automatic int i, j;
                i = $urandom_range(31, 0);
                j = $urandom_range(7, 0);
                case($urandom_range(9,0))
                    // external reg
                    0: cpuif.write('h100 + i*4, 'h100 + i);
                    1: cpuif.assert_read('h100 + i*4, 'h100 + i);
                    // internal reg
                    2: cpuif.write('h4, 'h1234);
                    3: cpuif.assert_read('h4, 'h1234);
                    // external regfile
                    4: cpuif.write('h1000 + j*4, 'h1000 + j);
                    5: cpuif.assert_read('h1000 + j*4, 'h1000 + j);
                    // external addrmap
                    6: cpuif.write('h2000 + j*4, 'h2000 + j);
                    7: cpuif.assert_read('h2000 + j*4, 'h2000 + j);
                    // external mem
                    8: cpuif.write('h3000 + j*4, 'h3000 + j);
                    9: cpuif.assert_read('h3000 + j*4, 'h3000 + j);
                endcase
            end
        join_none
    end
    wait fork;

{% endblock %}
