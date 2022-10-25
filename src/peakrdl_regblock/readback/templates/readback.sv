{% if array_assignments is not none %}
// Assign readback values to a flattened array
logic [{{cpuif.data_width-1}}:0] readback_array[{{array_size}}];
{{array_assignments}}


{%- if do_fanin_stage %}

// fanin stage
logic [{{cpuif.data_width-1}}:0] readback_array_c[{{fanin_array_size}}];
for(genvar g=0; g<{{fanin_loop_iter}}; g++) begin
    always_comb begin
        automatic logic [{{cpuif.data_width-1}}:0] readback_data_var;
        readback_data_var = '0;
        for(int i=g*{{fanin_stride}}; i<((g+1)*{{fanin_stride}}); i++) readback_data_var |= readback_array[i];
        readback_array_c[g] = readback_data_var;
    end
end
{%- if fanin_residual_stride == 1 %}
assign readback_array_c[{{fanin_array_size-1}}] = readback_array[{{array_size-1}}];
{%- elif fanin_residual_stride > 1 %}
always_comb begin
    automatic logic [{{cpuif.data_width-1}}:0] readback_data_var;
    readback_data_var = '0;
    for(int i={{(fanin_array_size-1) * fanin_stride}}; i<{{array_size}}; i++) readback_data_var |= readback_array[i];
    readback_array_c[{{fanin_array_size-1}}] = readback_data_var;
end
{%- endif %}

logic [{{cpuif.data_width-1}}:0] readback_array_r[{{fanin_array_size}}];
logic readback_done_r;
always_ff @(posedge clk) begin
    if(rst) begin
        for(int i=0; i<{{fanin_array_size}}; i++) readback_array_r[i] <= '0;
        readback_done_r <= '0;
    end else begin
        readback_array_r <= readback_array_c;
        readback_done_r <= decoded_req & ~decoded_req_is_wr;
    end
end

// Reduce the array
always_comb begin
    automatic logic [{{cpuif.data_width-1}}:0] readback_data_var;
    readback_done = readback_done_r;
    readback_err = '0;
    readback_data_var = '0;
    for(int i=0; i<{{fanin_array_size}}; i++) readback_data_var |= readback_array_r[i];
    readback_data = readback_data_var;
end

{%- else %}

// Reduce the array
always_comb begin
    automatic logic [{{cpuif.data_width-1}}:0] readback_data_var;
    readback_done = decoded_req & ~decoded_req_is_wr;
    readback_err = '0;
    readback_data_var = '0;
    for(int i=0; i<{{array_size}}; i++) readback_data_var |= readback_array[i];
    readback_data = readback_data_var;
end
{%- endif %}



{%- else %}
assign readback_done = decoded_req & ~decoded_req_is_wr;
assign readback_data = '0;
assign readback_err = '0;
{% endif %}
