interface axi4lite_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32
    )(
        input wire clk,
        input wire rst,
        axi4lite_intf.master m_axil
    );

    timeunit 1ps;
    timeprecision 1ps;

    logic AWREADY;
    logic AWVALID;
    logic [ADDR_WIDTH-1:0] AWADDR;
    logic [2:0] AWPROT;

    logic WREADY;
    logic WVALID;
    logic [DATA_WIDTH-1:0] WDATA;
    logic [DATA_WIDTH/8-1:0] WSTRB;

    logic BREADY;
    logic BVALID;
    logic [1:0] BRESP;

    logic ARREADY;
    logic ARVALID;
    logic [ADDR_WIDTH-1:0] ARADDR;
    logic [2:0] ARPROT;

    logic RREADY;
    logic RVALID;
    logic [DATA_WIDTH-1:0] RDATA;
    logic [1:0] RRESP;

    assign AWREADY = m_axil.AWREADY;
    assign m_axil.AWVALID = AWVALID;
    assign m_axil.AWADDR = AWADDR;
    assign m_axil.AWPROT = AWPROT;
    assign WREADY = m_axil.WREADY;
    assign m_axil.WVALID = WVALID;
    assign m_axil.WDATA = WDATA;
    assign m_axil.WSTRB = WSTRB;
    assign m_axil.BREADY = BREADY;
    assign BVALID = m_axil.BVALID;
    assign BRESP = m_axil.BRESP;
    assign ARREADY = m_axil.ARREADY;
    assign m_axil.ARVALID = ARVALID;
    assign m_axil.ARADDR = ARADDR;
    assign m_axil.ARPROT = ARPROT;
    assign m_axil.RREADY = RREADY;
    assign RVALID = m_axil.RVALID;
    assign RDATA = m_axil.RDATA;
    assign RRESP = m_axil.RRESP;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        input AWREADY;
        output AWVALID;
        output AWADDR;
        output AWPROT;
        input WREADY;
        output WVALID;
        output WDATA;
        output WSTRB;
        inout BREADY;
        input BVALID;
        input BRESP;
        input ARREADY;
        output ARVALID;
        output ARADDR;
        output ARPROT;
        inout RREADY;
        input RVALID;
        input RDATA;
        input RRESP;
    endclocking

    task automatic reset();
        cb.AWVALID <= '0;
        cb.AWADDR <= '0;
        cb.AWPROT <= '0;
        cb.WVALID <= '0;
        cb.WDATA <= '0;
        cb.WSTRB <= '0;
        cb.ARVALID <= '0;
        cb.ARADDR <= '0;
        cb.ARPROT <= '0;
    endtask

    initial forever begin
        cb.RREADY <= $urandom_range(1, 0);
        cb.BREADY <= $urandom_range(1, 0);
        @cb;
    end

    //--------------------------------------------------------------------------
    typedef struct {
        logic [1:0] bresp;
    } write_response_t;

    class write_request_t;
        mailbox #(write_response_t) response_mbx;
        logic [ADDR_WIDTH-1:0] addr;
        logic [DATA_WIDTH-1:0] data;
        logic [DATA_WIDTH/8-1:0] strb;
        function new();
            this.response_mbx = new();
        endfunction
    endclass

    mailbox #(write_request_t) aw_mbx = new();
    mailbox #(write_request_t) w_mbx = new();
    write_request_t write_queue[$];

    // Issue AW transfers
    initial forever begin
        write_request_t req;
        aw_mbx.get(req);
        ##0;
        repeat($urandom_range(2,0)) @cb;
        cb.AWVALID <= '1;
        cb.AWADDR <= req.addr;
        cb.AWPROT <= '0;
        @(cb);
        while(cb.AWREADY !== 1'b1) @(cb);
        cb.AWVALID <= '0;
    end

    // Issue W transfers
    initial forever begin
        write_request_t req;
        w_mbx.get(req);
        ##0;
        repeat($urandom_range(2,0)) @cb;
        cb.WVALID <= '1;
        cb.WDATA <= req.data;
        cb.WSTRB <= req.strb;
        @(cb);
        while(cb.WREADY !== 1'b1) @(cb);
        cb.WVALID <= '0;
        cb.WSTRB <= '0;
    end

    // Listen for R responses
    initial forever begin
        @cb;
        while(rst || !(cb.BREADY === 1'b1 && cb.BVALID === 1'b1)) @cb;
        if(write_queue.size() != 0) begin
            // Can match this response with an existing request.
            // Send response to requestor
            write_request_t req;
            write_response_t resp;
            req = write_queue.pop_front();
            resp.bresp = cb.BRESP;
            req.response_mbx.put(resp);
        end else begin
            $error("Got unmatched write response");
        end
    end

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, input logic [DATA_WIDTH/8-1:0] strb = {DATA_WIDTH{1'b1}}, logic expects_err = 1'b0);
        write_request_t req;
        write_response_t resp;

        req = new();
        req.addr = addr;
        req.data = data;
        req.strb = strb;

        aw_mbx.put(req);
        w_mbx.put(req);
        write_queue.push_back(req);

        // Wait for response
        req.response_mbx.get(resp);
        assert(!$isunknown(resp.bresp)) else $error("Write to 0x%0x returned X's on BRESP", addr);
        assert((resp.bresp==2'b10) == expects_err) else $error("Error write response to 0x%x returned 0x%x. Expected 0x%x", addr, (resp.bresp==2'b10), expects_err);
    endtask

    //--------------------------------------------------------------------------
    typedef struct {
        logic [DATA_WIDTH-1: 0] rdata;
        logic [1:0] rresp;
    } read_response_t;

    class read_request_t;
        mailbox #(read_response_t) response_mbx;
        function new();
            this.response_mbx = new();
        endfunction
    endclass

    semaphore txn_ar_mutex = new(1);
    read_request_t read_queue[$];

    // Listen for R responses
    initial forever begin
        @cb;
        while(rst || !(cb.RREADY === 1'b1 && cb.RVALID === 1'b1)) @cb;
        if(read_queue.size() != 0) begin
            // Can match this response with an existing request.
            // Send response to requestor
            read_request_t req;
            read_response_t resp;
            req = read_queue.pop_front();
            resp.rdata = cb.RDATA;
            resp.rresp = cb.RRESP;
            req.response_mbx.put(resp);
        end else begin
            $error("Got unmatched read response");
        end
    end

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, input logic expects_err = 1'b0);
        read_request_t req;
        read_response_t resp;

        txn_ar_mutex.get();
        // Issue read request
        ##0;
        cb.ARVALID <= '1;
        cb.ARADDR <= addr;
        cb.ARPROT <= '0;
        @(cb);
        while(cb.ARREADY !== 1'b1) @(cb);
        cb.ARVALID <= '0;

        // Push new request into queue
        req = new();
        read_queue.push_back(req);
        txn_ar_mutex.put();

        // Wait for response
        req.response_mbx.get(resp);

        assert(!$isunknown(resp.rdata)) else $error("Read from 0x%0x returned X's on RDATA", addr);
        assert(!$isunknown(resp.rresp)) else $error("Read from 0x%0x returned X's on RRESP", addr);
        assert((resp.rresp == 2'b10) == expects_err) else $error("Error read response from 0x%x returned 0x%x. Expected 0x%x", addr, (resp.rresp == 2'b10), expects_err);
        data = resp.rdata;
    endtask

    task automatic assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = {DATA_WIDTH{1'b1}}, input logic expects_err = 1'b0);
        logic [DATA_WIDTH-1:0] data;
        read(addr, data, expects_err);
        data &= mask;
        assert(data == expected_data) else $error("Read from 0x%x returned 0x%x. Expected 0x%x", addr, data, expected_data);
    endtask

    //--------------------------------------------------------------------------
    initial begin
        reset();
    end

    initial forever begin
        @cb;
        if(!rst) assert(!$isunknown(cb.AWREADY)) else $error("Saw X on AWREADY!");
        if(!rst) assert(!$isunknown(cb.WREADY)) else $error("Saw X on WREADY!");
        if(!rst) assert(!$isunknown(cb.BVALID)) else $error("Saw X on BVALID!");
        if(!rst) assert(!$isunknown(cb.ARREADY)) else $error("Saw X on ARREADY!");
        if(!rst) assert(!$isunknown(cb.RVALID)) else $error("Saw X on RVALID!");
    end

endinterface
