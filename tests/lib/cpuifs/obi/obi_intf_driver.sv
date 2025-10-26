interface obi_intf_driver #(
        parameter DATA_WIDTH = 32,
        parameter ADDR_WIDTH = 32,
        parameter ID_WIDTH = 1
    )(
        input wire clk,
        input wire rst,
        obi_intf.manager m_obi
    );

    timeunit 1ps;
    timeprecision 1ps;

    logic req;
    logic gnt;
    logic [ADDR_WIDTH-1:0] addr;
    logic we;
    logic [DATA_WIDTH/8-1:0] be;
    logic [DATA_WIDTH-1:0] wdata;
    logic [ID_WIDTH-1:0] aid;

    logic rvalid;
    logic rready;
    logic [DATA_WIDTH-1:0] rdata;
    logic err;
    logic [ID_WIDTH-1:0] rid;

    assign m_obi.req = req;
    assign gnt = m_obi.gnt;
    assign m_obi.addr = addr;
    assign m_obi.we = we;
    assign m_obi.be = be;
    assign m_obi.wdata = wdata;
    assign m_obi.aid = aid;

    assign rvalid = m_obi.rvalid;
    assign m_obi.rready = rready;
    assign rdata = m_obi.rdata;
    assign err = m_obi.err;
    assign rid = m_obi.rid;

    default clocking cb @(posedge clk);
        default input #1step output #1;
        output req;
        input gnt;
        output addr;
        output we;
        output be;
        output wdata;
        output aid;

        input rvalid;
        inout rready;
        input rdata;
        input err;
        input rid;
    endclocking

    task automatic reset();
        cb.req <= '0;
        cb.addr <= '0;
        cb.we <= '0;
        cb.be <= '0;
        cb.wdata <= '0;
        cb.aid <= '0;
    endtask

    initial forever begin
        cb.rready <= $urandom_range(1, 0);
        @cb;
    end

    //--------------------------------------------------------------------------
    typedef struct {
        logic [DATA_WIDTH-1:0] rdata;
        logic err;
        logic [ID_WIDTH-1:0] rid;
    } response_t;

    class request_t;
        mailbox #(response_t) response_mbx;
        logic [ID_WIDTH-1:0] aid;
        function new();
            this.response_mbx = new();
        endfunction
    endclass

    semaphore txn_req_mutex = new(1);
    request_t request_queue[$];

    // Listen for responses
    initial forever begin
        @cb;
        while(rst || !(cb.rready === 1'b1 && cb.rvalid === 1'b1)) @cb;
        if(request_queue.size() != 0) begin
            // Can match this response with an existing request.
            // Send response to requestor
            request_t req;
            response_t resp;
            req = request_queue.pop_front();
            resp.rdata = cb.rdata;
            resp.err = cb.err;
            resp.rid = cb.rid;

            assert(resp.rid == req.aid) else $error("Got incorrect RID! %0d != %0d", resp.rid, req.aid);

            req.response_mbx.put(resp);
        end else begin
            $error("Got unexpected response");
        end
    end

    //--------------------------------------------------------------------------
    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data, input logic expects_err = 1'b0);
        request_t req;
        response_t resp;
        logic [ID_WIDTH-1:0] id;

        txn_req_mutex.get();

        // Issue read request
        id = $urandom();
        ##0;
        cb.req <= '1;
        cb.we <= '0;
        cb.addr <= addr;
        cb.aid <= id;
        @(cb);
        while(cb.gnt !== 1'b1) @(cb);
        cb.req <= '0;

        // Push new request into queue
        req = new();
        req.aid = id;
        request_queue.push_back(req);
        txn_req_mutex.put();

        // Wait for response
        req.response_mbx.get(resp);

        assert(!$isunknown(resp.rdata)) else $error("Read from 0x%0x returned X's on rdata", addr);
        assert(!$isunknown(resp.err)) else $error("Read from 0x%0x returned X's on err", addr);
        assert(!$isunknown(resp.rid)) else $error("Read from 0x%0x returned X's on rid", addr);
        assert(resp.err == expects_err) else $error("Error read response from 0x%x returned 0x%x. Expected 0x%x", addr, resp.err, expects_err);
        data = resp.rdata;
    endtask

    task automatic assert_read(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] expected_data, logic [DATA_WIDTH-1:0] mask = {DATA_WIDTH{1'b1}}, input logic expects_err = 1'b0);
        logic [DATA_WIDTH-1:0] data;
        read(addr, data, expects_err);
        data &= mask;
        assert(data == expected_data) else $error("Read from 0x%x returned 0x%x. Expected 0x%x", addr, data, expected_data);
    endtask

    //--------------------------------------------------------------------------
    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data, logic [DATA_WIDTH/8-1:0] strb = {DATA_WIDTH{1'b1}}, input logic expects_err = 1'b0);
        request_t req;
        response_t resp;
        logic [ID_WIDTH-1:0] id;

        txn_req_mutex.get();

        // Issue write request
        id = $urandom();
        ##0;
        cb.req <= '1;
        cb.we <= '1;
        cb.be <= strb;
        cb.wdata <= data;
        cb.addr <= addr;
        cb.aid <= id;
        @(cb);
        while(cb.gnt !== 1'b1) @(cb);
        cb.req <= '0;

        // Push new request into queue
        req = new();
        req.aid = id;
        request_queue.push_back(req);
        txn_req_mutex.put();

        // Wait for response
        req.response_mbx.get(resp);

        assert(!$isunknown(resp.err)) else $error("Read from 0x%0x returned X's on err", addr);
        assert(!$isunknown(resp.rid)) else $error("Read from 0x%0x returned X's on rid", addr);
        assert(resp.err == expects_err) else $error("Error write response to 0x%x returned 0x%x. Expected 0x%x", addr, resp.err, expects_err);
    endtask

    //--------------------------------------------------------------------------
    initial begin
        reset();
    end

    initial forever begin
        @cb;
        if(!rst) assert(!$isunknown(cb.gnt)) else $error("Saw X on gnt!");
        if(!rst) assert(!$isunknown(cb.rvalid)) else $error("Saw X on rvalid!");
    end

endinterface
