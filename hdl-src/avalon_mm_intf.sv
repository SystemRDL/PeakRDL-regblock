interface avalon_mm_intf #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 32 // Important! Avalon uses word addressing
);
    // Command
    logic read;
    logic write;
    logic waitrequest;
    logic [ADDR_WIDTH-1:0] address;
    logic [DATA_WIDTH-1:0] writedata;
    logic [DATA_WIDTH/8-1:0] byteenable;

    // Response
    logic readdatavalid;
    logic writeresponsevalid;
    logic [DATA_WIDTH-1:0] readdata;
    logic [1:0] response;

    modport host (
        output read,
        output write,
        input waitrequest,
        output address,
        output writedata,
        output byteenable,

        input readdatavalid,
        input writeresponsevalid,
        input readdata,
        input response
    );

    modport agent (
        input read,
        input write,
        output waitrequest,
        input address,
        input writedata,
        input byteenable,

        output readdatavalid,
        output writeresponsevalid,
        output readdata,
        output response
    );
endinterface
