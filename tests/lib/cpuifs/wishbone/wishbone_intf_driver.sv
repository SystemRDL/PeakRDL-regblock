interface wishbone_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        input wire rst,
        wishbone_intf.host wb
    );
    timeunit 1ps;
    timeprecision 1ps;


    logic wb_cyc;
    logic wb_stb;
    logic wb_we;
    logic wb_stall;
    logic [ADDR_WIDTH-1:0] wb_adr;
    logic [DATA_WIDTH-1:0] wb_odat;
    logic [DATA_WIDTH/8-1:0] wb_sel;
    logic wb_ack;
    logic wb_err;
    logic [DATA_WIDTH-1:0] wb_idat;

    assign wb.cyc = wb_cyc;
    assign wb.stb = wb_stb;
    assign wb.we = wb_we;
    assign wb_stall = wb.stall;
    assign wb.adr = wb_adr;
    assign wb.odat = wb_odat;
    assign wb.sel = wb_sel;
    assign wb_ack = wb.ack;
    assign wb_err = wb.err;
    assign wb_idat = wb.idat;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output wb_cyc;
        output wb_stb;
        output wb_we;
        input wb_stall;
        output wb_adr;
        output wb_odat;
        output wb_sel;
        input wb_ack;
        input wb_err;
        input wb_idat;
    endclocking

    task automatic reset();
        cb.wb_cyc <= '0;
        cb.wb_stb <= '0;
        cb.wb_we <= '0;
        cb.wb_adr <= '0;
        cb.wb_odat <= '0;
        cb.wb_sel <= '0;
    endtask

    semaphore req_mutex = new(1);
    semaphore resp_mutex = new(1);

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH/8-1:0] strb = {DATA_WIDTH{1'b1}}, logic expects_err = 1'b0);
        fork
            begin
                req_mutex.get();
                ##0;
                // Initiate transfer
                cb.wb_stb <= '1;
                cb.wb_we <= '1;
                cb.wb_adr <= addr;
                cb.wb_odat <= data;
                cb.wb_sel <= strb;
                @(cb);

                // Wait for transfer to be accepted
                while(cb.wb_stall == 1'b1) @(cb);
                reset();
                req_mutex.put();
            end

            begin
                resp_mutex.get();
                @cb;
                // Wait for response
                while(cb.wb_ack !== 1'b1) @(cb);
                assert(!$isunknown(cb.wb_err)) else $error("Write to 0x%0x returned X's on wb_err", addr);
                resp_mutex.put();
            end
        join
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, input logic expects_err = 1'b0);
        fork
            begin
                req_mutex.get();
                ##0;
                // Initiate transfer
                cb.wb_stb <= '1;
                cb.wb_we <= '0;
                cb.wb_adr <= addr;
                @(cb);

                // Wait for transfer to be accepted
                while(cb.wb_stall == 1'b1) @(cb);
                reset();
                req_mutex.put();
            end

            begin
                resp_mutex.get();
                @cb;
                // Wait for response
                while(cb.wb_ack !== 1'b1) @(cb);
                assert(!$isunknown(cb.wb_err)) else $error("Read to 0x%0x returned X's on wb_err", addr);
                data = cb.wb_idat;
                resp_mutex.put();
            end
        join
    endtask

    task automatic assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = {DATA_WIDTH{1'b1}}, input logic expects_err = 1'b0);
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
        if(!rst) assert(!$isunknown(cb.wb_stall)) else $error("Saw X on wb_stall!");
        if(!rst) assert(!$isunknown(cb.wb_ack)) else $error("Saw X on wb_ack!");
        if(!rst) assert(!$isunknown(cb.wb_err)) else $error("Saw X on wb_err!");
    end

endinterface
