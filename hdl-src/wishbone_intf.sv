interface wishbone_intf #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 32
);
    // Command
    logic cyc;
    logic stb;
    logic we;
    logic stall;
    logic [ADDR_WIDTH-1:0] adr;
    logic [DATA_WIDTH-1:0] odat;
    logic [DATA_WIDTH/8-1:0] sel;

    // Response
    logic ack;
    logic err;
    logic [DATA_WIDTH-1:0] idat;

    modport host (
        output cyc,
        output stb,
        output we,
        input stall,
        output adr,
        output odat,
        output sel,

        input ack,
        input err,
        input idat
    );

    modport agent (
        input cyc,
        input stb,
        input we,
        output stall,
        input adr,
        input odat,
        input sel,

        output ack,
        output err,
        output idat
    );
endinterface
