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

    //--------------------------------------------------------------------------
    // CPU Bus interface logic
    //--------------------------------------------------------------------------
    logic cpuif_req;
    logic cpuif_req_is_wr;
    logic [{{cpuif.addr_width-1}}:0] cpuif_addr;
    logic [{{cpuif.data_width-1}}:0] cpuif_wr_data;
    logic [{{cpuif.data_width-1}}:0] cpuif_wr_biten;

    logic cpuif_rd_ack;
    logic [{{cpuif.data_width-1}}:0] cpuif_rd_data;
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
    logic [{{cpuif.data_width-1}}:0] decoded_wr_data;
    logic [{{cpuif.data_width-1}}:0] decoded_wr_biten;

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
    assign decoded_wr_biten = cpuif_wr_biten;

    //--------------------------------------------------------------------------
    // Field logic
    //--------------------------------------------------------------------------
    {{field_logic.get_combo_struct()|indent}}

    {{field_logic.get_storage_struct()|indent}}

    {{field_logic.get_implementation()|indent}}

    //--------------------------------------------------------------------------
    // Readback
    //--------------------------------------------------------------------------
    logic readback_err;
    logic readback_done;
    logic [{{cpuif.data_width-1}}:0] readback_data;
    {{readback.get_implementation()|indent}}

{% if retime_read_response %}
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{cpuif.reset.activehigh_identifier}}) begin
            cpuif_rd_ack <= '0;
            cpuif_rd_data <= '0;
            cpuif_rd_err <= '0;
        end else begin
            cpuif_rd_ack <= readback_done;
            cpuif_rd_data <= readback_data;
            cpuif_rd_err <= readback_err;
        end
    end
{% else %}
    assign cpuif_rd_ack = readback_done;
    assign cpuif_rd_data = readback_data;
    assign cpuif_rd_err = readback_err;
{% endif %}

endmodule
