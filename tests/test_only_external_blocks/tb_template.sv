{% extends "lib/tb_base.sv" %}



{%- block dut_support %}
    {% sv_line_anchor %}

    external_block #(
        .ADDR_WIDTH($clog2('h10))
    ) mem1_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mem1.req),
        .req_is_wr(hwif_out.mem1.req_is_wr),
        .addr(hwif_out.mem1.addr),
        .wr_data(hwif_out.mem1.wr_data),
        .wr_biten(hwif_out.mem1.wr_biten),
        .rd_ack(hwif_in.mem1.rd_ack),
        .rd_data(hwif_in.mem1.rd_data),
        .wr_ack(hwif_in.mem1.wr_ack)
    );

    external_block #(
        .ADDR_WIDTH($clog2('h90))
    ) mem2_inst (
        .clk(clk),
        .rst(rst),

        .req(hwif_out.mem2.req),
        .req_is_wr(hwif_out.mem2.req_is_wr),
        .addr(hwif_out.mem2.addr),
        .wr_data(hwif_out.mem2.wr_data),
        .wr_biten(hwif_out.mem2.wr_biten),
        .rd_ack(hwif_in.mem2.rd_ack),
        .rd_data(hwif_in.mem2.rd_data),
        .wr_ack(hwif_in.mem2.wr_ack)
    );

{%- endblock %}



{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##1;

    //--------------------------------------------------------------------------
    // Simple read/write tests
    //--------------------------------------------------------------------------
    // mem1
    repeat(32) begin
        logic [31:0] x;
        int unsigned addr;
        x = $urandom();
        addr = 'h0;
        addr += $urandom_range(('h10 / 4) - 1) * 4;
        cpuif.write(addr, x);
        cpuif.assert_read(addr, x);
    end

    // mem2
    repeat(32) begin
        logic [31:0] x;
        int unsigned addr;
        x = $urandom();
        addr = 'h200;
        addr += $urandom_range(('h90 / 4) - 1) * 4;
        cpuif.write(addr, x);
        cpuif.assert_read(addr, x);
    end

    //--------------------------------------------------------------------------
    // Pipelined access
    //--------------------------------------------------------------------------
    // init array with unique known value
    for(int i=0; i<('h10 / 4); i++) begin
        cpuif.write('h0 + i*4, 'h1000 + i);
    end
    for(int i=0; i<('h90 / 4); i++) begin
        cpuif.write('h200 + i*4, 'h3000 + i);
    end

    // random pipelined read/writes
    repeat(256) begin
        fork
            begin
                int i;
                logic [31:0] x;
                int unsigned addr;
                case($urandom_range(1))
                    0: begin
                        i = $urandom_range(('h10 / 4) - 1);
                        x = 'h1000 + i;
                        addr = 'h0 + i*4;
                    end
                    1: begin
                        i = $urandom_range(('h90 / 4) - 1);
                        x = 'h3000 + i;
                        addr = 'h200 + i*4;
                    end
                endcase

                case($urandom_range(1))
                    0: cpuif.write(addr, x);
                    1: cpuif.assert_read(addr, x);
                endcase
            end
        join_none
    end
    wait fork;

{% endblock %}
