interface ahb_intf #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 32
);
    // Command
    logic HSEL;
    logic HWRITE;
    logic [1:0] HTRANS;
    logic [2:0] HSIZE;
    logic [ADDR_WIDTH-1:0] HADDR;
    logic [DATA_WIDTH-1:0] HWDATA;

    // Response
    logic [DATA_WIDTH-1:0] HRDATA;
    logic HREADY;
    logic HRESP;

    modport master (
        output HSEL,
        output HWRITE,
        output HTRANS,
        output HSIZE,
        output HADDR,
        output HWDATA,

        input HRDATA,
        input HREADY,
        input HRESP
    );

    modport slave (
        input HSEL,
        input HWRITE,
        input HTRANS,
        input HSIZE,
        input HADDR,
        input HWDATA,

        output HRDATA,
        output HREADY,
        output HRESP
    );
endinterface

