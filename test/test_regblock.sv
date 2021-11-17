// TODO: Add a banner
module test_regblock (
        input wire clk,
        input wire rst,

        apb3_intf.slave s_apb,

        output test_regblock_pkg::test_regblock__out_t hwif_out
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
            end else begin
                if(~is_active) begin
                    if(s_apb.PSEL) begin
                        is_active <= '1;
                        cpuif_req <= '1;
                        cpuif_req_is_wr <= s_apb.PWRITE;
                        cpuif_addr <= s_apb.PADDR[ADDR_WIDTH-1:0];
                        cpuif_wr_data <= s_apb.PWDATA;
                    end
                end else begin
                    cpuif_req <= '0;
                    if(cpuif_rd_ack || cpuif_wr_ack) begin
                        is_active <= '0;
                    end
                end
            end
        end
        assign cpuif_wr_bitstrb = '0;

        // Response
        assign s_apb.PREADY = cpuif_rd_ack | cpuif_wr_ack;
        assign s_apb.PRDATA = cpuif_rd_data;
        assign s_apb.PSLVERR = cpuif_rd_err | cpuif_wr_err;
    end

    //--------------------------------------------------------------------------
    // Address Decode
    //--------------------------------------------------------------------------
    typedef struct {
        logic r0;
        logic r1;
        logic r2;
    } decoded_reg_strb_t;
    decoded_reg_strb_t decoded_reg_strb;
    logic decoded_req;
    logic decoded_req_is_wr;
    logic [DATA_WIDTH-1:0] decoded_wr_data;
    logic [DATA_WIDTH-1:0] decoded_wr_bitstrb;

    always_comb begin
        decoded_reg_strb.r0 = cpuif_req & (cpuif_addr == 'h0);
        decoded_reg_strb.r1 = cpuif_req & (cpuif_addr == 'h100);
        decoded_reg_strb.r2 = cpuif_req & (cpuif_addr == 'h200);
    end

    // Writes are always granted with no error response
    assign cpuif_wr_ack = cpuif_req & cpuif_req_is_wr;
    assign cpuif_wr_err = '0;

    // Pass down signals to next stage
    assign decoded_req = cpuif_req;
    assign decoded_req_is_wr = cpuif_req_is_wr;
    assign decoded_wr_data = cpuif_wr_data;
    assign decoded_wr_bitstrb = cpuif_wr_bitstrb;

    //--------------------------------------------------------------------------
    // Field logic
    //--------------------------------------------------------------------------
    typedef struct {
        struct {
            struct {
                logic [7:0] next;
                logic load_next;
            } a;
            struct {
                logic [7:0] next;
                logic load_next;
            } b;
            struct {
                logic [7:0] next;
                logic load_next;
            } c;
        } r0;
        struct {
            struct {
                logic [7:0] next;
                logic load_next;
            } a;
            struct {
                logic [7:0] next;
                logic load_next;
            } b;
            struct {
                logic [7:0] next;
                logic load_next;
            } c;
        } r1;
        struct {
            struct {
                logic [7:0] next;
                logic load_next;
            } a;
            struct {
                logic [7:0] next;
                logic load_next;
            } b;
            struct {
                logic [7:0] next;
                logic load_next;
            } c;
        } r2;
    } field_combo_t;
    field_combo_t field_combo;

    typedef struct {
        struct {
            logic [7:0] a;
            logic [7:0] b;
            logic [7:0] c;
        } r0;
        struct {
            logic [7:0] a;
            logic [7:0] b;
            logic [7:0] c;
        } r1;
        struct {
            logic [7:0] a;
            logic [7:0] b;
            logic [7:0] c;
        } r2;
    } field_storage_t;
    field_storage_t field_storage;

    // Field: test_regblock.r0.a
    always_comb begin
        field_combo.r0.a.next = field_storage.r0.a;
        field_combo.r0.a.load_next = '0;
        if(decoded_reg_strb.r0 && decoded_req_is_wr) begin // SW write
            field_combo.r0.a.next = decoded_wr_data[7:0];
            field_combo.r0.a.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r0.a <= 'h10;
        end else if(field_combo.r0.a.load_next) begin
            field_storage.r0.a <= field_combo.r0.a.next;
        end
    end
    assign hwif_out.r0.a.value = field_storage.r0.a;
    assign hwif_out.r0.a.anded = &(field_storage.r0.a);
    // Field: test_regblock.r0.b
    always_comb begin
        field_combo.r0.b.next = field_storage.r0.b;
        field_combo.r0.b.load_next = '0;
        if(decoded_reg_strb.r0 && decoded_req_is_wr) begin // SW write
            field_combo.r0.b.next = decoded_wr_data[15:8];
            field_combo.r0.b.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r0.b <= 'h20;
        end else if(field_combo.r0.b.load_next) begin
            field_storage.r0.b <= field_combo.r0.b.next;
        end
    end
    assign hwif_out.r0.b.value = field_storage.r0.b;
    assign hwif_out.r0.b.ored = |(field_storage.r0.b);
    // Field: test_regblock.r0.c
    always_comb begin
        field_combo.r0.c.next = field_storage.r0.c;
        field_combo.r0.c.load_next = '0;
        if(decoded_reg_strb.r0 && decoded_req_is_wr) begin // SW write
            field_combo.r0.c.next = decoded_wr_data[23:16];
            field_combo.r0.c.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r0.c <= 'h30;
        end else if(field_combo.r0.c.load_next) begin
            field_storage.r0.c <= field_combo.r0.c.next;
        end
    end
    assign hwif_out.r0.c.value = field_storage.r0.c;
    assign hwif_out.r0.c.swmod = decoded_reg_strb.r0 && decoded_req_is_wr;
    // Field: test_regblock.r1.a
    always_comb begin
        field_combo.r1.a.next = field_storage.r1.a;
        field_combo.r1.a.load_next = '0;
        if(decoded_reg_strb.r1 && decoded_req_is_wr) begin // SW write
            field_combo.r1.a.next = decoded_wr_data[7:0];
            field_combo.r1.a.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r1.a <= 'h10;
        end else if(field_combo.r1.a.load_next) begin
            field_storage.r1.a <= field_combo.r1.a.next;
        end
    end
    assign hwif_out.r1.a.value = field_storage.r1.a;
    assign hwif_out.r1.a.anded = &(field_storage.r1.a);
    // Field: test_regblock.r1.b
    always_comb begin
        field_combo.r1.b.next = field_storage.r1.b;
        field_combo.r1.b.load_next = '0;
        if(decoded_reg_strb.r1 && decoded_req_is_wr) begin // SW write
            field_combo.r1.b.next = decoded_wr_data[15:8];
            field_combo.r1.b.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r1.b <= 'h20;
        end else if(field_combo.r1.b.load_next) begin
            field_storage.r1.b <= field_combo.r1.b.next;
        end
    end
    assign hwif_out.r1.b.value = field_storage.r1.b;
    assign hwif_out.r1.b.ored = |(field_storage.r1.b);
    // Field: test_regblock.r1.c
    always_comb begin
        field_combo.r1.c.next = field_storage.r1.c;
        field_combo.r1.c.load_next = '0;
        if(decoded_reg_strb.r1 && decoded_req_is_wr) begin // SW write
            field_combo.r1.c.next = decoded_wr_data[23:16];
            field_combo.r1.c.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r1.c <= 'h30;
        end else if(field_combo.r1.c.load_next) begin
            field_storage.r1.c <= field_combo.r1.c.next;
        end
    end
    assign hwif_out.r1.c.value = field_storage.r1.c;
    assign hwif_out.r1.c.swmod = decoded_reg_strb.r1 && decoded_req_is_wr;
    // Field: test_regblock.r2.a
    always_comb begin
        field_combo.r2.a.next = field_storage.r2.a;
        field_combo.r2.a.load_next = '0;
        if(decoded_reg_strb.r2 && decoded_req_is_wr) begin // SW write
            field_combo.r2.a.next = decoded_wr_data[7:0];
            field_combo.r2.a.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r2.a <= 'h10;
        end else if(field_combo.r2.a.load_next) begin
            field_storage.r2.a <= field_combo.r2.a.next;
        end
    end
    assign hwif_out.r2.a.value = field_storage.r2.a;
    assign hwif_out.r2.a.anded = &(field_storage.r2.a);
    // Field: test_regblock.r2.b
    always_comb begin
        field_combo.r2.b.next = field_storage.r2.b;
        field_combo.r2.b.load_next = '0;
        if(decoded_reg_strb.r2 && decoded_req_is_wr) begin // SW write
            field_combo.r2.b.next = decoded_wr_data[15:8];
            field_combo.r2.b.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r2.b <= 'h20;
        end else if(field_combo.r2.b.load_next) begin
            field_storage.r2.b <= field_combo.r2.b.next;
        end
    end
    assign hwif_out.r2.b.value = field_storage.r2.b;
    assign hwif_out.r2.b.ored = |(field_storage.r2.b);
    // Field: test_regblock.r2.c
    always_comb begin
        field_combo.r2.c.next = field_storage.r2.c;
        field_combo.r2.c.load_next = '0;
        if(decoded_reg_strb.r2 && decoded_req_is_wr) begin // SW write
            field_combo.r2.c.next = decoded_wr_data[23:16];
            field_combo.r2.c.load_next = '1;
        end
    end
    always_ff @(posedge clk) begin
        if(rst) begin
            field_storage.r2.c <= 'h30;
        end else if(field_combo.r2.c.load_next) begin
            field_storage.r2.c <= field_combo.r2.c.next;
        end
    end
    assign hwif_out.r2.c.value = field_storage.r2.c;
    assign hwif_out.r2.c.swmod = decoded_reg_strb.r2 && decoded_req_is_wr;

    //--------------------------------------------------------------------------
    // Readback
    //--------------------------------------------------------------------------
    
    logic readback_err;
    logic readback_done;
    logic [DATA_WIDTH-1:0] readback_data;
    logic [DATA_WIDTH-1:0] readback_array[3];

    assign readback_array[0][7:0] = (decoded_reg_strb.r0 && !decoded_req_is_wr) ? field_storage.r0.a : '0;
    assign readback_array[0][15:8] = (decoded_reg_strb.r0 && !decoded_req_is_wr) ? field_storage.r0.b : '0;
    assign readback_array[0][23:16] = (decoded_reg_strb.r0 && !decoded_req_is_wr) ? field_storage.r0.c : '0;
    assign readback_array[0][31:24] = '0;
    assign readback_array[1][7:0] = (decoded_reg_strb.r1 && !decoded_req_is_wr) ? field_storage.r1.a : '0;
    assign readback_array[1][15:8] = (decoded_reg_strb.r1 && !decoded_req_is_wr) ? field_storage.r1.b : '0;
    assign readback_array[1][23:16] = (decoded_reg_strb.r1 && !decoded_req_is_wr) ? field_storage.r1.c : '0;
    assign readback_array[1][31:24] = '0;
    assign readback_array[2][7:0] = (decoded_reg_strb.r2 && !decoded_req_is_wr) ? field_storage.r2.a : '0;
    assign readback_array[2][15:8] = (decoded_reg_strb.r2 && !decoded_req_is_wr) ? field_storage.r2.b : '0;
    assign readback_array[2][23:16] = (decoded_reg_strb.r2 && !decoded_req_is_wr) ? field_storage.r2.c : '0;
    assign readback_array[2][31:24] = '0;

    always_comb begin
        automatic logic [DATA_WIDTH-1:0] readback_data_var;
        readback_done = decoded_req & ~decoded_req_is_wr;
        readback_err = '0;

        readback_data_var = '0;
        for(int i=0; i<3; i++) begin
            readback_data_var |= readback_array[i];
        end
        readback_data = readback_data_var;
    end

    always_ff @(posedge clk) begin
        if(rst) begin
            cpuif_rd_ack <= '0;
            cpuif_rd_data <= '0;
            cpuif_rd_err <= '0;
        end else begin
            cpuif_rd_ack <= readback_done;
            cpuif_rd_data <= readback_data;
            cpuif_rd_err <= readback_err;
        end
    end

endmodule