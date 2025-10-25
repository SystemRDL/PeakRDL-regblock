interface apb4_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        input wire rst,
        apb4_intf.master m_apb
    );

    timeunit 1ps;
    timeprecision 1ps;

    logic PSEL;
    logic PENABLE;
    logic PWRITE;
    logic [2:0] PPROT;
    logic [ADDR_WIDTH-1:0] PADDR;
    logic [DATA_WIDTH-1:0] PWDATA;
    logic [DATA_WIDTH/8-1:0] PSTRB;
    logic [DATA_WIDTH-1:0] PRDATA;
    logic PREADY;
    logic PSLVERR;

    assign m_apb.PSEL = PSEL;
    assign m_apb.PENABLE = PENABLE;
    assign m_apb.PWRITE = PWRITE;
    assign m_apb.PPROT = PPROT;
    assign m_apb.PADDR = PADDR;
    assign m_apb.PWDATA = PWDATA;
    assign m_apb.PSTRB = PSTRB;
    assign PRDATA = m_apb.PRDATA;
    assign PREADY = m_apb.PREADY;
    assign PSLVERR = m_apb.PSLVERR;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output PSEL;
        output PENABLE;
        output PWRITE;
        output PPROT;
        output PADDR;
        output PWDATA;
        output PSTRB;
        input PRDATA;
        input PREADY;
        input PSLVERR;
    endclocking

    task automatic reset();
        cb.PSEL <= '0;
        cb.PENABLE <= '0;
        cb.PWRITE <= '0;
        cb.PPROT <= '0;
        cb.PADDR <= '0;
        cb.PWDATA <= '0;
        cb.PSTRB <= '0;
    endtask

    semaphore txn_mutex = new(1);

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH/8-1:0] strb = {DATA_WIDTH{1'b1}}, logic expects_err = 0);
        txn_mutex.get();
        ##0;

        // Initiate transfer
        cb.PSEL <= '1;
        cb.PENABLE <= '0;
        cb.PWRITE <= '1;
        cb.PPROT <= '0;
        cb.PADDR <= addr;
        cb.PWDATA <= data;
        cb.PSTRB <= strb;
        @(cb);

        // active phase
        cb.PENABLE <= '1;
        @(cb);

        // Wait for response
        while(cb.PREADY !== 1'b1) @(cb);
        assert(!$isunknown(cb.PSLVERR)) else $error("Write to 0x%0x returned X's on PSLVERR", addr);
        assert(cb.PSLVERR == expects_err) else $error("Error write response to 0x%x returned 0x%x. Expected 0x%x", addr, cb.PSLVERR, expects_err);
        reset();
        txn_mutex.put();
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, input logic expects_err = 0);
        txn_mutex.get();
        ##0;

        // Initiate transfer
        cb.PSEL <= '1;
        cb.PENABLE <= '0;
        cb.PWRITE <= '0;
        cb.PPROT <= '0;
        cb.PADDR <= addr;
        cb.PWDATA <= '0;
        cb.PSTRB <= '0;
        @(cb);

        // active phase
        cb.PENABLE <= '1;
        @(cb);

        // Wait for response
        while(cb.PREADY !== 1'b1) @(cb);
        assert(!$isunknown(cb.PRDATA)) else $error("Read from 0x%0x returned X's on PRDATA", addr);
        assert(!$isunknown(cb.PSLVERR)) else $error("Read from 0x%0x returned X's on PSLVERR", addr);
        assert(cb.PSLVERR == expects_err) else $error("Error read response from 0x%x returned 0x%x. Expected 0x%x", addr, cb.PSLVERR, expects_err);
        data = cb.PRDATA;
        reset();
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
        if(!rst) assert(!$isunknown(cb.PREADY)) else $error("Saw X on PREADY!");
    end

endinterface
