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

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH-1:0] biten = '1);
        logic wr_err;
        write_err(addr,data,biten,wr_err);
    endtask

    task automatic write_err(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH-1:0] biten = '1, output logic wr_err);
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
                wr_err = cb.m_cpuif_wr_err;
                txn_resp_mutex.put();
            end
        join
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data);
        logic rd_err;
        read_err(addr,data,rd_err);
    endtask

    task automatic read_err(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, output logic rd_err);
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
                data = cb.m_cpuif_rd_data;
                rd_err = cb.m_cpuif_rd_err;
                txn_resp_mutex.put();
            end
        join
    endtask

    task automatic assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = '1);
        logic [DATA_WIDTH-1:0] data;
        read(addr, data);
        data &= mask;
        assert(data == expected_data) else $error("Read from 0x%x returned 0x%x. Expected 0x%x", addr, data, expected_data);
    endtask

    task automatic assert_read_err(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic expected_rd_err, logic [DATA_WIDTH-1:0] mask = '1);
        logic [DATA_WIDTH-1:0] data;
        logic                  rd_err;
        read_err(addr, data,rd_err);
        data &= mask;
        assert(data == expected_data) else $error("Read from 0x%x returned 0x%x. Expected 0x%x", addr, data, expected_data);
        assert(rd_err == expected_rd_err) else $error("Error read response from 0x%x returned 0x%x. Expected 0x%x", addr, rd_err, expected_rd_err);
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
