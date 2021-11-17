interface apb3_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        apb3_intf.master m_apb
    );

    timeunit 1ps;
    timeprecision 1ps;

    logic PSEL;
    logic PENABLE;
    logic PWRITE;
    logic [ADDR_WIDTH-1:0] PADDR;
    logic [DATA_WIDTH-1:0] PWDATA;
    logic [DATA_WIDTH-1:0] PRDATA;
    logic PREADY;
    logic PSLVERR;

    assign m_apb.PSEL = PSEL;
    assign m_apb.PENABLE = PENABLE;
    assign m_apb.PWRITE = PWRITE;
    assign m_apb.PADDR = PADDR;
    assign m_apb.PWDATA = PWDATA;
    assign PRDATA = m_apb.PRDATA;
    assign PREADY = m_apb.PREADY;
    assign PSLVERR = m_apb.PSLVERR;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output PSEL;
        output PENABLE;
        output PWRITE;
        output PADDR;
        output PWDATA;
        input PRDATA;
        input PREADY;
        input PSLVERR;
    endclocking

    task reset();
        cb.PSEL <= '0;
        cb.PENABLE <= '0;
        cb.PWRITE <= '0;
        cb.PADDR <= '0;
        cb.PWDATA <= '0;
    endtask

    task write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data);
        ##0;

        // Initiate transfer
        cb.PSEL <= '1;
        cb.PENABLE <= '0;
        cb.PWRITE <= '1;
        cb.PADDR <= addr;
        cb.PWDATA <= data;
        @(cb);

        // active phase
        cb.PENABLE <= '1;
        @(cb);

        // Wait for response
        while(cb.PREADY !== 1'b1) @(cb);
        reset();
    endtask

    task read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data);
        ##0;

        // Initiate transfer
        cb.PSEL <= '1;
        cb.PENABLE <= '0;
        cb.PWRITE <= '0;
        cb.PADDR <= addr;
        cb.PWDATA <= '0;
        @(cb);

        // active phase
        cb.PENABLE <= '1;
        @(cb);

        // Wait for response
        while(cb.PREADY !== 1'b1) @(cb);
        data = cb.PRDATA;
        reset();
    endtask

    initial begin
        reset();
    end

endinterface
