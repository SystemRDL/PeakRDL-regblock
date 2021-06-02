// Hand-coded demo. Not auto-generated

package top_pkg;

    // top.whee[][].y
    typedef struct {
        logic value;
    } top__wheexx__y__out_t;

    // top.whee[][]
    typedef struct {
        top__wheexx__y__out_t y;
    } top__wheexx__out_t;

    // top.asdf[].aaa[].abc
    typedef struct {
        logic [14:0] value;
    } top__asdfx__aaax__abc__out_t;

    // top.asdf[].aaa[].def
    typedef struct {
        logic [3:0] value;
    } top__asdfx__aaax__def__out_t;

    // top.asdf[].aaa[]
    typedef struct {
        top__asdfx__aaax__abc__out_t abc;
        top__asdfx__aaax__def__out_t def;
    } top__asdfx__aaax__out_t;

    // top.asdf[].bbb.abc
    typedef struct {
        logic value;
    } top__asdfx__bbb__abc__out_t;

    // top.asdf[].bbb.def
    typedef struct {
        logic value;
    } top__asdfx__bbb__def__out_t;

    // top.asdf[].bbb
    typedef struct {
        top__asdfx__bbb__abc__out_t abc;
        top__asdfx__bbb__def__out_t def;
    } top__asdfx__bbb__out_t;

    // top.asdf[]
    typedef struct {
        top__asdfx__aaax__out_t aaa[4];
        top__asdfx__bbb__out_t bbb;
    } top__asdfx__out_t;

    // top
    typedef struct {
        top__wheexx__out_t whee[2][8];
        top__asdfx__out_t asdf[20];
    } top__out_t;

endpackage

module top #(
        // TODO: pipeline parameters
    )(
        input wire clk,
        input wire rst,


        apb4_intf.slave s_apb,

        output top_pkg::top__out_t hwif_out
    );

    localparam ADDR_WIDTH = 32;
    localparam DATA_WIDTH = 32;

    //--------------------------------------------------------------------------
    // CPU Bus interface logic
    //--------------------------------------------------------------------------
    logic cpuif_req;
    logic cpuif_req_is_wr;
    logic [ADDR_WIDTH-1:0] cpuif_addr;
    logic [DATA_WIDTH-1:0] cpuif_wr_data;
    logic [DATA_WIDTH-1:0] cpuif_wr_bitstrb;

    logic cpuif_rd_ack;
    logic [DATA_WIDTH-1:0] cpuif_rd_data;
    logic cpuif_rd_err;

    logic cpuif_wr_ack;
    logic cpuif_wr_err;

    begin
        // Request
        logic is_active;
        always_ff @(posedge clk) begin
            if(rst) begin
                is_active <= '0;
                cpuif_req <= '0;
                cpuif_req_is_wr <= '0;
                cpuif_addr <= '0;
                cpuif_wr_data <= '0;
                cpuif_wr_bitstrb <= '0;
            end else begin
                if(~is_active) begin
                    if(s_apb.psel) begin
                        is_active <= '1;
                        cpuif_req <= '1;
                        cpuif_req_is_wr <= s_apb.pwrite;
                        cpuif_addr <= s_apb.paddr[ADDR_WIDTH-1:0];
                        cpuif_wr_data <= s_apb.pwdata;
                        for(int i=0; i<DATA_WIDTH/8; i++) begin
                            cpuif_wr_bitstrb[i*8 +: 8] <= {8{s_apb.pstrb[i]}};
                        end
                    end
                end else begin
                    cpuif_req <= '0;
                    if(cpuif_rd_ack || cpuif_wr_ack) begin
                        is_active <= '0;
                    end
                end
            end
        end

        // Response
        assign s_apb.pready = cpuif_rd_ack | cpuif_wr_ack;
        assign s_apb.prdata = cpuif_rd_data;
        assign s_apb.pslverr = cpuif_rd_err | cpuif_wr_err;
    end

    //--------------------------------------------------------------------------
    // Address Decode
    //--------------------------------------------------------------------------
    typedef struct {
        logic whee[2][8];
        struct {
            logic aaa[4];
            logic bbb;
        } asdf[20];
    } access_strb_t;
    access_strb_t access_strb;

    always_comb begin
        for(int i0=0; i0<2; i0++) begin
            for(int i1=0; i1<8; i1++) begin
                access_strb.whee[i0][i1] = cpuif_req & (cpuif_addr == 'h0 + i0*'h20 + i1*'h4);
            end
        end
        for(int i0=0; i0<20; i0++) begin
            for(int i1=0; i1<4; i1++) begin
                access_strb.asdf[i0].aaa[i1] = cpuif_req & (cpuif_addr == 'h40 + i0*'h14 + i1*'h4);
            end
            access_strb.asdf[i0].bbb = cpuif_req & (cpuif_addr == 'h50 + i0*'h14);
        end
    end

    // Writes are always posted with no error response
    assign cpuif_wr_ack = cpuif_req & cpuif_req_is_wr;
    assign cpuif_wr_err = '0;

    //--------------------------------------------------------------------------
    // Field logic
    //--------------------------------------------------------------------------
    typedef struct {
        struct {
            logic y;
        } whee[2][8];
        struct {
            struct {
                logic [14:0] abc;
                logic [3:0] def;
            } aaa[4];
            struct {
                logic abc;
                logic def;
            } bbb;
        } asdf[20];
    } field_storage_t;
    field_storage_t field_storage;

    // TODO: Field next-state logic, and output port signal assignment (aka output mapping layer)
    TODO:

    //--------------------------------------------------------------------------
    // Readback mux
    //--------------------------------------------------------------------------
    logic readback_err;
    logic [DATA_WIDTH-1:0] readback_data;

    always_comb begin
        readback_err = '0;
        readback_data = '0;
        if(cpuif_req & ~cpuif_req_is_wr) begin
            readback_err = '1;
            for(int i0=0; i0<2; i0++) begin
                for(int i1=0; i1<8; i1++) begin
                    if(cpuif_addr == 'h0 + i0*'h20 + i1*'h4) begin
                        readback_err = '0;
                        readback_data[0:0] = field_storage.whee[i0][i1].y;
                    end
                end
            end
            for(int i0=0; i0<20; i0++) begin
                for(int i1=0; i1<4; i1++) begin
                    if(cpuif_addr == 'h40 + i0*'h14 + i1*'h4) begin
                        readback_err = '0;
                        readback_data[16:2] = field_storage.asdf[i0].aaa[i1].abc;
                        readback_data[4:4] = field_storage.asdf[i0].aaa[i1].def;
                    end
                end
                if(cpuif_addr == 'h50 + i0*'h14) begin
                    readback_err = '0;
                    readback_data[0:0] = field_storage.asdf[i0].bbb.abc;
                    readback_data[1:1] = field_storage.asdf[i0].bbb.def;
                end
            end
        end
    end

    assign cpuif_rd_ack = cpuif_req & ~cpuif_req_is_wr;
    assign cpuif_rd_data = readback_data;
    assign cpuif_rd_err = readback_err;

endmodule
