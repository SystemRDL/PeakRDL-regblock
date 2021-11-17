{% if array_assignments is not none %}
logic readback_err;
logic readback_done;
logic [DATA_WIDTH-1:0] readback_data;
logic [DATA_WIDTH-1:0] readback_array[{{array_size}}];

{{array_assignments}}

always_comb begin
    automatic logic [DATA_WIDTH-1:0] readback_data_var;
    readback_done = decoded_req & ~decoded_req_is_wr;
    readback_err = '0;

    readback_data_var = '0;
    for(int i=0; i<{{array_size}}; i++) begin
        readback_data_var |= readback_array[i];
    end
    readback_data = readback_data_var;
end

always_ff {{get_always_ff_event(cpuif_reset)}} begin
    if({{cpuif_reset.activehigh_identifier}}) begin
        cpuif_rd_ack <= '0;
        cpuif_rd_data <= '0;
        cpuif_rd_err <= '0;
    end else begin
        cpuif_rd_ack <= readback_done;
        cpuif_rd_data <= readback_data;
        cpuif_rd_err <= readback_err;
    end
end



{%- else %}
always_ff {{get_always_ff_event(cpuif_reset)}} begin
    if({{cpuif_reset.activehigh_identifier}}) begin
        cpuif_rd_ack <= '0;
    end else begin
        cpuif_rd_ack <= decoded_req & ~decoded_req_is_wr;
    end
end
assign cpuif_rd_data = '0;
assign cpuif_rd_err = '0;
{% endif %}
