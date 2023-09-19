module external_block #(
    parameter WIDTH = 32,
    parameter ADDR_WIDTH = 8
)(
    input logic clk,
    input logic rst,

    input logic req,
    input logic req_is_wr,
    input logic [ADDR_WIDTH-1:0] addr,
    input logic [WIDTH-1:0] wr_data,
    input logic [WIDTH-1:0] wr_biten,
    output logic rd_ack,
    output logic [WIDTH-1:0] rd_data,
    output logic wr_ack
);
timeunit 1ns;
timeprecision 1ps;

localparam ADDR_SHIFT = $clog2(WIDTH/8);
localparam N_ENTRIES = 2**(ADDR_WIDTH - ADDR_SHIFT);
logic [WIDTH-1:0] mem[N_ENTRIES];


task do_write(int idx, logic [WIDTH-1:0] data, logic [WIDTH-1:0] biten);
    automatic int delay;
    // Random delay
    delay = $urandom_range(3,0);
    repeat(delay) @(posedge clk)
    $info("Write delay: %d", delay);

    for(int b=0; b<WIDTH; b++) begin
        if(biten[b]) mem[idx][b] <= data[b];
    end
    wr_ack <= '1;
endtask

task do_read(int idx);
    automatic int delay;
    // Random delay
    delay = $urandom_range(3,0);
    repeat(delay) @(posedge clk)
    $info("Read delay: %d", delay);

    rd_data <= mem[idx];
    rd_ack <= '1;
endtask;


initial begin
    rd_ack <= '0;
    rd_data <= '0;
    wr_ack <= '0;
    for(int i=0; i<N_ENTRIES; i++) mem[i] <= '0;

    forever begin
        // Wait for next clock edge
        @(posedge clk);
        rd_ack <= '0;
        rd_data <= '0;
        wr_ack <= '0;

        // wait slightly longer to "peek" at the current cycle's state
        #1ns;

        if(!rst && req) begin
            if(req_is_wr) do_write(addr >> ADDR_SHIFT, wr_data, wr_biten);
            else do_read(addr >> ADDR_SHIFT);
        end
    end
end

endmodule
