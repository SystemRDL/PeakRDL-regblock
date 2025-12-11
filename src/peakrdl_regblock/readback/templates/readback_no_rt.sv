always_comb begin
    automatic logic [{{cpuif.data_width-1}}:0] readback_data_var;
    readback_data_var = '0;
    {{readback_mux|indent}}
    readback_data = readback_data_var;

    {%- if ds.has_external_addressable %}
    readback_done = decoded_req & ~decoded_req_is_wr & ~decoded_req_is_external;
    {%- else %}
    readback_done = decoded_req & ~decoded_req_is_wr;
    {%- endif %}
    {%- if ds.err_if_bad_addr or ds.err_if_bad_rw %}
    readback_err = decoded_err;
    {%- else %}
    readback_err = '0;
    {%- endif %}
end
