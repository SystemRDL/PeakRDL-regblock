interface obi_intf #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 32,
    parameter ID_WIDTH = 1
);
    logic req;
    logic gnt;
    logic [ADDR_WIDTH-1:0] addr;
    logic we;
    logic [DATA_WIDTH/8-1:0] be;
    logic [DATA_WIDTH-1:0] wdata;
    logic [ID_WIDTH-1:0] aid;

    logic rvalid;
    logic rready;
    logic [DATA_WIDTH-1:0] rdata;
    logic err;
    logic [ID_WIDTH-1:0] rid;

    modport manager (
        output req,
        input gnt,
        output addr,
        output we,
        output be,
        output wdata,
        output aid,

        input rvalid,
        output rready,
        input rdata,
        input err,
        input rid
    );

    modport subordinate (
        input req,
        output gnt,
        input addr,
        input we,
        input be,
        input wdata,
        input aid,

        output rvalid,
        input rready,
        output rdata,
        output err,
        output rid
    );
endinterface
