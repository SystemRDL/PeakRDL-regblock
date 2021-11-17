// TODO: Add a banner
module {{module_name}} (
        input wire clk,
        {%- for signal in reset_signals %}
        {{signal.port_declaration}},
        {%- endfor %}

        {%- for signal in user_signals %}
        {{signal.port_declaration}},
        {%- endfor %}

        {%- for interrupt in interrupts %}
        {{interrupt.port_declaration}},
        {%- endfor %}

        {{cpuif.port_declaration|indent(8)}}
        {%- if hwif.has_input_struct or hwif.has_output_struct %},{% endif %}

        {{hwif.port_declaration|indent(8)}}
    );

    localparam ADDR_WIDTH = {{addr_width}};
    localparam DATA_WIDTH = {{data_width}};

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

    {{cpuif.get_implementation()|indent}}

    //--------------------------------------------------------------------------
    // Address Decode
    //--------------------------------------------------------------------------
    {{address_decode.get_strobe_struct()|indent}}
    decoded_reg_strb_t decoded_reg_strb;
    logic decoded_req;
    logic decoded_req_is_wr;
    logic [DATA_WIDTH-1:0] decoded_wr_data;
    logic [DATA_WIDTH-1:0] decoded_wr_bitstrb;

    always_comb begin
        {{address_decode.get_implementation()|indent(8)}}
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
    {{field_logic.get_combo_struct()|indent}}

    {{field_logic.get_storage_struct()|indent}}

    {{field_logic.get_implementation()|indent}}

    //--------------------------------------------------------------------------
    // Readback
    //--------------------------------------------------------------------------
    {{readback.get_implementation()|indent}}

endmodule
