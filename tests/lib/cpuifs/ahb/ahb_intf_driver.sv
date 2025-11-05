interface ahb_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        input wire rst,
        ahb_intf.master m_ahb
    );

    timeunit 1ps;
    timeprecision 1ps;

    // AHB Transfer Types
    localparam [1:0] HTRANS_IDLE   = 2'b00;
    localparam [1:0] HTRANS_NONSEQ = 2'b10;

    // AHB Size encodings
    localparam [2:0] HSIZE_BYTE  = 3'b000;
    localparam [2:0] HSIZE_HWORD = 3'b001;
    localparam [2:0] HSIZE_WORD  = 3'b010;
    localparam [2:0] HSIZE_DWORD = 3'b011;

    logic HSEL;
    logic HWRITE;
    logic [1:0] HTRANS;
    logic [2:0] HSIZE;
    logic [ADDR_WIDTH-1:0] HADDR;
    logic [DATA_WIDTH-1:0] HWDATA;
    logic [DATA_WIDTH-1:0] HRDATA;
    logic HREADY;
    logic HRESP;

    assign m_ahb.HSEL = HSEL;
    assign m_ahb.HWRITE = HWRITE;
    assign m_ahb.HTRANS = HTRANS;
    assign m_ahb.HSIZE = HSIZE;
    assign m_ahb.HADDR = HADDR;
    assign m_ahb.HWDATA = HWDATA;
    assign HRDATA = m_ahb.HRDATA;
    assign HREADY = m_ahb.HREADY;
    assign HRESP = m_ahb.HRESP;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output HSEL;
        output HWRITE;
        output HTRANS;
        output HSIZE;
        output HADDR;
        output HWDATA;
        input HRDATA;
        input HREADY;
        input HRESP;
    endclocking

    task automatic reset();
        cb.HSEL <= '0;
        cb.HWRITE <= '0;
        cb.HTRANS <= HTRANS_IDLE;
        cb.HSIZE <= HSIZE_WORD;
        cb.HADDR <= '0;
        cb.HWDATA <= '0;
    endtask

    semaphore txn_mutex = new(1);

    // Helper function to determine HSIZE based on data width
    function automatic [2:0] get_hsize();
        case(DATA_WIDTH)
            8:       return HSIZE_BYTE;
            16:      return HSIZE_HWORD;
            32:      return HSIZE_WORD;
            64:      return HSIZE_DWORD;
            default: return HSIZE_WORD;
        endcase
    endfunction

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH/8-1:0] strb = '1, logic expects_err = 0);
        txn_mutex.get();
        ##0;

        // Address Phase
        cb.HSEL <= '1;
        cb.HWRITE <= '1;
        cb.HTRANS <= HTRANS_NONSEQ;
        cb.HSIZE <= get_hsize();
        cb.HADDR <= addr;
        @(cb);

        // Data Phase - provide write data and set HTRANS to IDLE
        cb.HWDATA <= data;
        cb.HTRANS <= HTRANS_IDLE;
        
        // Wait for HREADY - must wait at least one cycle for data phase
        do @(cb); while(cb.HREADY !== 1'b1);
        
        // Check for error response
        assert(!$isunknown(cb.HRESP)) else $error("Write to 0x%0x returned X's on HRESP", addr);
        assert(cb.HRESP == expects_err) else $error("Error write response to 0x%x returned 0x%x. Expected 0x%x", addr, cb.HRESP, expects_err);
        
        reset();
        // Wait one more cycle to ensure is_active resets before next transaction
        @(cb);
        txn_mutex.put();
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, input logic expects_err = 0);
        logic [DATA_WIDTH-1:0] data_local;
        txn_mutex.get();
        ##0;

        // Address Phase
        cb.HSEL <= '1;
        cb.HWRITE <= '0;
        cb.HTRANS <= HTRANS_NONSEQ;
        cb.HSIZE <= get_hsize();
        cb.HADDR <= addr;
        cb.HWDATA <= '0;
        @(cb);

        // Data Phase - set HTRANS to IDLE
        cb.HTRANS <= HTRANS_IDLE;
        @(cb);

        // Wait for HREADY
        while(cb.HREADY !== 1'b1) @(cb);
        
        // Sample data and check for errors
        assert(!$isunknown(cb.HRDATA)) else $error("Read from 0x%0x returned X's on HRDATA", addr);
        assert(!$isunknown(cb.HRESP)) else $error("Read from 0x%0x returned X's on HRESP", addr);
        assert(cb.HRESP == expects_err) else $error("Error read response from 0x%x returned 0x%x. Expected 0x%x", addr, cb.HRESP, expects_err);
        
        data = cb.HRDATA;
        
        reset();
        // Wait one more cycle to ensure is_active resets before next transaction  
        @(cb);
                
        txn_mutex.put();
    endtask

    task automatic assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = {DATA_WIDTH{1'b1}}, input logic expects_err = 0);
        logic [DATA_WIDTH-1:0] data;
        read(addr, data, expects_err);
        data &= mask;
        assert(data == expected_data) else $error("Read from 0x%x returned 0x%x. Expected 0x%x", addr, data, expected_data);
    endtask

    initial begin
        reset();
    end

    initial forever begin
        @cb;
        if(!rst) assert(!$isunknown(cb.HREADY)) else $error("Saw X on HREADY!");
    end

endinterface

