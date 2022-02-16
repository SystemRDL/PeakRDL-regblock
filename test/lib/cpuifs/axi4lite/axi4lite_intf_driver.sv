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

    semaphore txn_aw_mutex = new(1);
    semaphore txn_w_mutex = new(1);
    semaphore txn_b_mutex = new(1);
    semaphore txn_ar_mutex = new(1);
    semaphore txn_r_mutex = new(1);

    task automatic write(logic [ADDR_WIDTH-1:0] addr, logic [DATA_WIDTH-1:0] data);
        bit w_before_aw;
        w_before_aw = $urandom_range(1,0);

        fork
            begin
                txn_aw_mutex.get();
                ##0;
                if(w_before_aw) repeat($urandom_range(2,0)) @cb;
                cb.AWVALID <= '1;
                cb.AWADDR <= addr;
                cb.AWPROT <= '0;
                @(cb);
                while(cb.AWREADY !== 1'b1) @(cb);
                cb.AWVALID <= '0;
                txn_aw_mutex.put();
            end

            begin
                txn_w_mutex.get();
                ##0;
                if(!w_before_aw) repeat($urandom_range(2,0)) @cb;
                cb.WVALID <= '1;
                cb.WDATA <= data;
                cb.WSTRB <= '1; // TODO: Support byte strobes
                @(cb);
                while(cb.WREADY !== 1'b1) @(cb);
                cb.WVALID <= '0;
                cb.WSTRB <= '0;
                txn_w_mutex.put();
            end

            begin
                txn_b_mutex.get();
                @cb;
                while(!(cb.BREADY === 1'b1 && cb.BVALID === 1'b1)) @(cb);
                assert(!$isunknown(cb.BRESP)) else $error("Read from 0x%0x returned X's on BRESP", addr);
                txn_b_mutex.put();
            end
        join
    endtask

    task automatic read(logic [ADDR_WIDTH-1:0] addr, output logic [DATA_WIDTH-1:0] data);

        fork
            begin
                txn_ar_mutex.get();
                ##0;
                cb.ARVALID <= '1;
                cb.ARADDR <= addr;
                cb.ARPROT <= '0;
                @(cb);
                while(cb.ARREADY !== 1'b1) @(cb);
                cb.ARVALID <= '0;
                txn_ar_mutex.put();
            end

            begin
                txn_r_mutex.get();
                @cb;
                while(!(cb.RREADY === 1'b1 && cb.RVALID === 1'b1)) @(cb);
                assert(!$isunknown(cb.RDATA)) else $error("Read from 0x%0x returned X's on RDATA", addr);
                assert(!$isunknown(cb.RRESP)) else $error("Read from 0x%0x returned X's on RRESP", addr);
                data = cb.RDATA;
                txn_r_mutex.put();
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
        if(!rst) assert(!$isunknown(cb.AWREADY)) else $error("Saw X on AWREADY!");
        if(!rst) assert(!$isunknown(cb.WREADY)) else $error("Saw X on WREADY!");
        if(!rst) assert(!$isunknown(cb.BVALID)) else $error("Saw X on BVALID!");
        if(!rst) assert(!$isunknown(cb.ARREADY)) else $error("Saw X on ARREADY!");
        if(!rst) assert(!$isunknown(cb.RVALID)) else $error("Saw X on RVALID!");
    end

endinterface
