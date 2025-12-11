assign readback_done = decoded_req & ~decoded_req_is_wr;
assign readback_data = '0;
{%- if ds.err_if_bad_addr or ds.err_if_bad_rw %}
assign readback_err = decoded_err;
{%- else %}
assign readback_err = '0;
{%- endif %}
