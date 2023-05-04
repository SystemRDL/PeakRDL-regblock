module external_reg #(
    parameter WIDTH = 32,
    parameter SUBWORDS = 1
)(
    input wire clk,
    input wire rst,

    input wire [SUBWORDS-1:0] req,
    input wire req_is_wr,
    input wire [WIDTH-1:0] wr_data,
    input wire [WIDTH-1:0] wr_biten,
    output logic rd_ack,
    output logic [WIDTH-1:0] rd_data,
    output logic wr_ack
);
timeunit 1ns;
timeprecision 1ps;
logic [SUBWORDS-1:0][WIDTH-1:0] value;


task do_write(logic [SUBWORDS-1:0] strb, logic [WIDTH-1:0] data, logic [WIDTH-1:0] biten);
    automatic int delay;
    // Random delay
    delay = $urandom_range(3,0);
    repeat(delay) @(posedge clk)
    $info("Write delay: %d", delay);

    for(int i=0; i<SUBWORDS; i++) begin
        if(strb[i]) begin
            for(int b=0; b<WIDTH; b++) begin
                if(biten[b]) value[i][b] <= data[b];
            end
        end
    end
    wr_ack <= '1;
endtask

task do_read(logic [SUBWORDS-1:0] strb);
    automatic int delay;
    // Random delay
    delay = $urandom_range(3,0);
    repeat(delay) @(posedge clk)
    $info("Read delay: %d", delay);


    for(int i=0; i<SUBWORDS; i++) begin
        if(strb[i]) begin
            rd_data <= value[i];
        end
    end
    rd_ack <= '1;
endtask;


initial begin
    rd_ack <= '0;
    rd_data <= '0;
    wr_ack <= '0;
    value <= '0;

    forever begin
        // Wait for next clock edge
        @(posedge clk);
        rd_ack <= '0;
        rd_data <= '0;
        wr_ack <= '0;

        // wait slightly longer to "peek" at the current cycle's state
        #1ns;

        if(!rst && req) begin
            if(req_is_wr) do_write(req, wr_data, wr_biten);
            else do_read(req);
        end
    end
end

endmodule
