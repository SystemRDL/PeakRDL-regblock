// TODO: Add a banner
module test_regblock (
        input wire clk,
        input wire rst,

        apb3_intf.slave s_apb,

        output test_regblock_pkg::test_regblock__out_t hwif_out
    );

    //--------------------------------------------------------------------------
    // CPU Bus interface logic
    //--------------------------------------------------------------------------
    logic cpuif_req;
    logic cpuif_req_is_wr;
    logic [10:0] cpuif_addr;
    logic [31:0] cpuif_wr_data;
    logic [31:0] cpuif_wr_biten;

    logic cpuif_rd_ack;
    logic [31:0] cpuif_rd_data;
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
                        cpuif_addr <= {s_apb.PADDR[10:2], 2'b0};
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
        assign cpuif_wr_biten = '1;

        // Response
        assign s_apb.PREADY = cpuif_rd_ack | cpuif_wr_ack;
        assign s_apb.PRDATA = cpuif_rd_data;
        assign s_apb.PSLVERR = cpuif_rd_err | cpuif_wr_err;
    end

    //--------------------------------------------------------------------------
    // Address Decode
    //--------------------------------------------------------------------------
    typedef struct {
        logic r2[112];
    } decoded_reg_strb_t;
    decoded_reg_strb_t decoded_reg_strb;
    logic decoded_req;
    logic decoded_req_is_wr;
    logic [31:0] decoded_wr_data;
    logic [31:0] decoded_wr_biten;

    always_comb begin
        for(int i0=0; i0<112; i0++) begin
            decoded_reg_strb.r2[i0] = cpuif_req & (cpuif_addr == 'h200 + i0*'h8);
        end
    end

    // Writes are always granted with no error response
    assign cpuif_wr_ack = cpuif_req & cpuif_req_is_wr;
    assign cpuif_wr_err = '0;

    // Pass down signals to next stage
    assign decoded_req = cpuif_req;
    assign decoded_req_is_wr = cpuif_req_is_wr;
    assign decoded_wr_data = cpuif_wr_data;
    assign decoded_wr_biten = cpuif_wr_biten;

    //--------------------------------------------------------------------------
    // Field logic
    //--------------------------------------------------------------------------
    typedef struct {
        struct {
            struct {
                logic [7:0] next;
                logic load_next;
            } a;
        } r2[112];
    } field_combo_t;
    field_combo_t field_combo;

    typedef struct {
        struct {
            logic [7:0] a;
        } r2[112];
    } field_storage_t;
    field_storage_t field_storage;

    for(genvar i0=0; i0<112; i0++) begin
        // Field: test_regblock.r2[].a
        always_comb begin
            field_combo.r2[i0].a.next = field_storage.r2[i0].a;
            field_combo.r2[i0].a.load_next = '0;
            if(decoded_reg_strb.r2[i0] && decoded_req_is_wr) begin // SW write
                field_combo.r2[i0].a.next = decoded_wr_data[7:0];
                field_combo.r2[i0].a.load_next = '1;
            end
        end
        always_ff @(posedge clk) begin
            if(rst) begin
                field_storage.r2[i0].a <= 'h10;
            end else if(field_combo.r2[i0].a.load_next) begin
                field_storage.r2[i0].a <= field_combo.r2[i0].a.next;
            end
        end
        assign hwif_out.r2[i0].a.value = field_storage.r2[i0].a;
        assign hwif_out.r2[i0].a.anded = &(field_storage.r2[i0].a);
    end

    //--------------------------------------------------------------------------
    // Readback
    //--------------------------------------------------------------------------
    logic readback_err;
    logic readback_done;
    logic [31:0] readback_data;
    
    // Assign readback values to a flattened array
    logic [31:0] readback_array[112];
    for(genvar i0=0; i0<112; i0++) begin
        assign readback_array[i0*1 + 0][7:0] = (decoded_reg_strb.r2[i0] && !decoded_req_is_wr) ? field_storage.r2[i0].a : '0;
        assign readback_array[i0*1 + 0][31:8] = '0;
    end


    // Reduce the array
    always_comb begin
        automatic logic [31:0] readback_data_var;
        readback_done = decoded_req & ~decoded_req_is_wr;
        readback_err = '0;
        readback_data_var = '0;
        for(int i=0; i<112; i++) readback_data_var |= readback_array[i];
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