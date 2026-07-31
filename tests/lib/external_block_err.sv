module external_block_err #(
    parameter WIDTH = 32,
    parameter ADDR_WIDTH = 8
)(
    input wire clk,
    input wire rst,

    input wire req,
    input wire req_is_wr,
    input wire [ADDR_WIDTH-1:0] addr,
    input wire [WIDTH-1:0] wr_data,
    input wire [WIDTH-1:0] wr_biten,
    output logic rd_ack,
    output logic [WIDTH-1:0] rd_data,
    output logic rd_err,
    output logic wr_ack,
    output logic wr_err
);
timeunit 1ps;
timeprecision 1ps;

localparam ADDR_SHIFT = $clog2(WIDTH/8);

task do_write(int idx, logic [WIDTH-1:0] data, logic [WIDTH-1:0] biten);
    automatic int delay;
    // Random delay
    delay = $urandom_range(3,0);
    repeat(delay) @(posedge clk)
    $info("Write delay: %d", delay);

    wr_ack <= '1;
    wr_err <= '1;
endtask

task do_read(int idx);
    automatic int delay;
    // Random delay
    delay = $urandom_range(3,0);
    repeat(delay) @(posedge clk)
    $info("Read delay: %d", delay);

    rd_ack <= '1;
    rd_err <= '1;
endtask;


initial begin
    rd_ack <= '0;
    rd_data <= '0;
    wr_ack <= '0;
    rd_err <= '0;
    wr_err <= '0;

    forever begin
        // Wait for next clock edge
        @(posedge clk);
        rd_ack <= '0;
        rd_data <= '0;
        wr_ack <= '0;
        rd_err <= '0;
        wr_err <= '0;

        // wait slightly longer to "peek" at the current cycle's state
        #1ns;

        if(!rst && req) begin
            if(req_is_wr) do_write(addr >> ADDR_SHIFT, wr_data, wr_biten);
            else do_read(addr >> ADDR_SHIFT);
        end
    end
end

endmodule
