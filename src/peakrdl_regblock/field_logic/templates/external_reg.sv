{% if retime -%}


always_ff {{get_always_ff_event(resetsignal)}} begin
    if({{get_resetsignal(resetsignal)}}) begin
        {{prefix}}.req <= '0;
        {{prefix}}.req_is_wr <= '0;
        {{prefix}}.wr_data <= '0;
        {{prefix}}.wr_biten <= '0;
    end else begin
        {{prefix}}.req <= {{strb}};
        {{prefix}}.req_is_wr <= decoded_req_is_wr;
        {{prefix}}.wr_data <= decoded_wr_data{{bslice}};
        {{prefix}}.wr_biten <= decoded_wr_biten{{bslice}};
    end
end


{%- else -%}


assign {{prefix}}.req = {{strb}};
assign {{prefix}}.req_is_wr = decoded_req_is_wr;
assign {{prefix}}.wr_data = decoded_wr_data{{bslice}};
assign {{prefix}}.wr_biten = decoded_wr_biten{{bslice}};


{%- endif %}
