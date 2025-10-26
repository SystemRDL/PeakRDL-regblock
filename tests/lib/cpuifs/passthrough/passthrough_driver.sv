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
        output logic [DATA_WIDTH-1:0] m_cpuif_wr_biten,
        input wire m_cpuif_req_stall_wr,
        input wire m_cpuif_req_stall_rd,
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
        output m_cpuif_wr_biten;
        input m_cpuif_req_stall_wr;
        input m_cpuif_req_stall_rd;
        input m_cpuif_rd_ack;
        input m_cpuif_rd_err;
        input m_cpuif_rd_data;
        input m_cpuif_wr_ack;
        input m_cpuif_wr_err;
    endclocking

    task automatic reset();
        cb.m_cpuif_req <= '0;
        cb.m_cpuif_req_is_wr <= '0;
        cb.m_cpuif_addr <= '0;
        cb.m_cpuif_wr_data <= '0;
        cb.m_cpuif_wr_biten <= '0;
    endtask

    semaphore txn_req_mutex = new(1);
    semaphore txn_resp_mutex = new(1);

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH-1:0] biten = {DATA_WIDTH{1'b1}}, logic expects_err = 1'b0);
        fork
            begin
                // Initiate transfer
                txn_req_mutex.get();
                ##0;
                cb.m_cpuif_req <= '1;
                cb.m_cpuif_req_is_wr <= '1;
                cb.m_cpuif_addr <= addr;
                cb.m_cpuif_wr_data <= data;
                cb.m_cpuif_wr_biten <= biten;
                @(cb);
                while(cb.m_cpuif_req_stall_wr !== 1'b0) @(cb);
                reset();
                txn_req_mutex.put();
            end

            begin
                // Wait for response
                txn_resp_mutex.get();
                @cb;
                while(cb.m_cpuif_wr_ack !== 1'b1) @(cb);
                assert(cb.m_cpuif_wr_err == expects_err) else $error("Error write response to 0x%x returned 0x%x. Expected 0x%x", addr, cb.m_cpuif_wr_err, expects_err);
                txn_resp_mutex.put();
            end
        join
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, input logic expects_err = 1'b0);
        fork
            begin
                // Initiate transfer
                txn_req_mutex.get();
                ##0;
                cb.m_cpuif_req <= '1;
                cb.m_cpuif_req_is_wr <= '0;
                cb.m_cpuif_addr <= addr;
                @(cb);
                while(cb.m_cpuif_req_stall_rd !== 1'b0) @(cb);
                reset();
                txn_req_mutex.put();
            end

            begin
                // Wait for response
                txn_resp_mutex.get();
                @cb;
                while(cb.m_cpuif_rd_ack !== 1'b1) @(cb);
                assert(!$isunknown(cb.m_cpuif_rd_data)) else $error("Read from 0x%0x returned X's on m_cpuif_rd_data", addr);
                assert(cb.m_cpuif_rd_err == expects_err) else $error("Error read response from 0x%x returned 0x%x. Expected 0x%x", addr, cb.m_cpuif_rd_err, expects_err);
                data = cb.m_cpuif_rd_data;
                txn_resp_mutex.put();
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
        if(!rst) assert(!$isunknown(cb.m_cpuif_rd_ack)) else $error("Saw X on m_cpuif_rd_ack!");
        if(!rst) assert(!$isunknown(cb.m_cpuif_wr_ack)) else $error("Saw X on m_cpuif_wr_ack!");
    end

endinterface
