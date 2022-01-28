interface passthrough_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        input wire rst,

        output logic m_cpuif_req,
        output logic m_cpuif_req_is_wr,
        output logic [ADDR_WIDTH-1:0] m_cpuif_addr,
        output logic [DATA_WIDTH-1:0] m_cpuif_wr_data,
        input wire m_cpuif_rd_ack,
        input wire m_cpuif_rd_err,
        input wire [DATA_WIDTH-1:0] m_cpuif_rd_data,
        input wire m_cpuif_wr_ack,
        input wire m_cpuif_wr_err
    );

    timeunit 1ps;
    timeprecision 1ps;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output m_cpuif_req;
        output m_cpuif_req_is_wr;
        output m_cpuif_addr;
        output m_cpuif_wr_data;
        input m_cpuif_rd_ack;
        input m_cpuif_rd_err;
        input m_cpuif_rd_data;
        input m_cpuif_wr_ack;
        input m_cpuif_wr_err;
    endclocking

    task reset();
        cb.m_cpuif_req <= '0;
        cb.m_cpuif_req_is_wr <= '0;
        cb.m_cpuif_addr <= '0;
        cb.m_cpuif_wr_data <= '0;
    endtask

    task write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data);
        ##0;

        // Initiate transfer
        cb.m_cpuif_req <= '1;
        cb.m_cpuif_req_is_wr <= '1;
        cb.m_cpuif_addr <= addr;
        cb.m_cpuif_wr_data <= data;
        @(cb);
        reset();

        // Wait for response
        while(cb.m_cpuif_wr_ack !== 1'b1) @(cb);
        reset();
    endtask

    task read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data);
        ##0;

        // Initiate transfer
        cb.m_cpuif_req <= '1;
        cb.m_cpuif_req_is_wr <= '0;
        cb.m_cpuif_addr <= addr;
        @(cb);
        reset();

        // Wait for response
        while(cb.m_cpuif_rd_ack !== 1'b1) @(cb);
        assert(!$isunknown(cb.m_cpuif_rd_data)) else $error("Read from 0x%0x returned X's on m_cpuif_rd_data", addr);
        data = cb.m_cpuif_rd_data;
        reset();
    endtask

    task assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = '1);
        logic [DATA_WIDTH-1:0] data;
        read(addr, data);
        data &= mask;
        assert(data == expected_data) else $error("Read from 0x%x returned 0x%x. Expected 0x%x", addr, data, expected_data);
    endtask

    initial begin
        reset();
    end

    initial forever begin
        @cb;
        if(!rst) assert(!$isunknown(cb.m_cpuif_rd_ack)) else $error("Saw X on m_cpuif_rd_ack!");
        if(!rst) assert(!$isunknown(cb.m_cpuif_wr_ack)) else $error("Saw X on m_cpuif_wr_ack!");
    end

endinterface
