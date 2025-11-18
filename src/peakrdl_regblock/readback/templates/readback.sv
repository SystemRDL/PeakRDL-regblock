{% if array_assignments is not none %}
// Assign readback values to a flattened array
logic [{{cpuif.data_width-1}}:0] readback_array[{{array_size}}];
{{array_assignments}}


{%- if ds.retime_read_fanin %}

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
logic readback_err_r;
always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        for(int i=0; i<{{fanin_array_size}}; i++) readback_array_r[i] <= '0;
        readback_done_r <= '0;
        readback_err_r <= '0;
    end else begin
        readback_array_r <= readback_array_c;
        readback_err_r <= decoded_err;
        {%- if ds.has_external_addressable %}
        readback_done_r <= decoded_req & ~decoded_req_is_wr & ~decoded_strb_is_external;
        {%- else %}
        readback_done_r <= decoded_req & ~decoded_req_is_wr;
        {%- endif %}
    end
end

// Reduce the array
always_comb begin
    readback_done = readback_done_r;
    {%- if ds.err_if_bad_addr or ds.err_if_bad_rw %}
    readback_err = readback_err_r;
    readback_data = decoded_err ? '0 : readback_array[cpuif_index];
    {%- else %}
    readback_err = '0;
    readback_data = readback_array[cpuif_index];
    {%- endif %}
end

{%- else %}

// Reduce the array
always_comb begin
    {%- if ds.has_external_addressable %}
    readback_done = decoded_req & ~decoded_req_is_wr & ~decoded_strb_is_external;
    {%- else %}
    readback_done = decoded_req & ~decoded_req_is_wr;
    {%- endif %}
    {%- if ds.err_if_bad_addr or ds.err_if_bad_rw %}
    readback_err = decoded_err;
    readback_data = decoded_err ? '0 : readback_array[cpuif_index];
    {%- else %}
    readback_err = '0;
    readback_data = readback_array[cpuif_index];
    {%- endif %}
end
{%- endif %}



{%- else %}
assign readback_done = decoded_req & ~decoded_req_is_wr;
assign readback_data = '0;
{%- if ds.err_if_bad_addr or ds.err_if_bad_rw %}
assign readback_err = decoded_err;
{%- else %}
assign readback_err = '0;
{%- endif %}
{% endif %}
