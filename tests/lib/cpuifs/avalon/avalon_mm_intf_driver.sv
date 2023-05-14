interface avalon_mm_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        input wire rst,
        avalon_mm_intf.host avalon
    );
    localparam ADDR_PAD = $clog2(DATA_WIDTH/8);
    localparam WORD_ADDR_WIDTH = ADDR_WIDTH - ADDR_PAD;

    timeunit 1ps;
    timeprecision 1ps;

    logic av_read;
    logic av_write;
    logic av_waitrequest;
    logic [WORD_ADDR_WIDTH-1:0] av_address;
    logic [DATA_WIDTH-1:0] av_writedata;
    logic [DATA_WIDTH/8-1:0] av_byteenable;
    logic av_readdatavalid;
    logic av_writeresponsevalid;
    logic [DATA_WIDTH-1:0] av_readdata;
    logic [1:0] av_response;

    assign avalon.read = av_read;
    assign avalon.write = av_write;
    assign av_waitrequest = avalon.waitrequest;
    assign avalon.address = av_address;
    assign avalon.writedata = av_writedata;
    assign avalon.byteenable = av_byteenable;
    assign av_readdatavalid = avalon.readdatavalid;
    assign av_writeresponsevalid = avalon.writeresponsevalid;
    assign av_readdata = avalon.readdata;
    assign av_response = avalon.response;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output av_read;
        output av_write;
        input av_waitrequest;
        output av_address;
        output av_writedata;
        output av_byteenable;
        input av_readdatavalid;
        input av_writeresponsevalid;
        input av_readdata;
        input av_response;
    endclocking

    task automatic reset();
        cb.av_read <= '0;
        cb.av_write <= '0;
        cb.av_address <= '0;
        cb.av_writedata <= '0;
        cb.av_byteenable <= '0;
    endtask

    semaphore req_mutex = new(1);
    semaphore resp_mutex = new(1);

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH/8-1:0] strb = '1);
        fork
            begin
                req_mutex.get();
                ##0;
                // Initiate transfer
                cb.av_write <= '1;
                cb.av_address <= (addr >> ADDR_PAD);
                cb.av_writedata <= data;
                cb.av_byteenable <= strb;
                @(cb);

                // Wait for transfer to be accepted
                while(cb.av_waitrequest == 1'b1) @(cb);
                reset();
                req_mutex.put();
            end

            begin
                resp_mutex.get();
                @cb;
                // Wait for response
                while(cb.av_writeresponsevalid !== 1'b1) @(cb);
                assert(!$isunknown(cb.av_response)) else $error("Read from 0x%0x returned X's on av_response", addr);
                resp_mutex.put();
            end
        join
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data);
        fork
            begin
                req_mutex.get();
                ##0;
                // Initiate transfer
                cb.av_read <= '1;
                cb.av_address <= (addr >> ADDR_PAD);
                @(cb);

                // Wait for transfer to be accepted
                while(cb.av_waitrequest == 1'b1) @(cb);
                reset();
                req_mutex.put();
            end

            begin
                resp_mutex.get();
                @cb;
                // Wait for response
                while(cb.av_readdatavalid !== 1'b1) @(cb);
                assert(!$isunknown(cb.av_readdata)) else $error("Read from 0x%0x returned X's on av_response", av_readdata);
                assert(!$isunknown(cb.av_response)) else $error("Read from 0x%0x returned X's on av_response", addr);
                data = cb.av_readdata;
                resp_mutex.put();
            end
        join
    endtask

    task automatic assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = '1);
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
        if(!rst) assert(!$isunknown(cb.av_waitrequest)) else $error("Saw X on av_waitrequest!");
        if(!rst) assert(!$isunknown(cb.av_readdatavalid)) else $error("Saw X on av_readdatavalid!");
        if(!rst) assert(!$isunknown(cb.av_writeresponsevalid)) else $error("Saw X on av_writeresponsevalid!");
    end

endinterface
