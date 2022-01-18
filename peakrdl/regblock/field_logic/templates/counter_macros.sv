{% macro up_counter(field) -%}
    if({{field_logic.get_counter_incr_strobe(node)}}) begin // increment
        {%- if field_logic.counter_incrsaturates(node) %}
        if((({{node.width+1}})'(next_c) + {{field_logic.get_counter_incrvalue(node)}}) > {{field_logic.get_counter_incrsaturate_value(node)}}) begin // up-counter saturated
            next_c = {{field_logic.get_counter_incrsaturate_value(node)}};
        end else begin
            next_c = next_c + {{field_logic.get_counter_incrvalue(node)}};
        end
        {%- else %}
        {{field_logic.get_field_combo_identifier(node, "overflow")}} = ((({{node.width+1}})'(next_c) + {{field_logic.get_counter_incrvalue(node)}}) > {{get_value(2**node.width - 1)}});
        next_c = next_c + {{field_logic.get_counter_incrvalue(node)}};
        {%- endif %}
        load_next_c = '1;
    {%- if not field_logic.counter_incrsaturates(node) %}
    end else begin
        {{field_logic.get_field_combo_identifier(node, "overflow")}} = '0;
    {%- endif %}
    end
    {{field_logic.get_field_combo_identifier(node, "incrthreshold")}} = ({{field_logic.get_storage_identifier(node)}} >= {{field_logic.get_counter_incrthreshold_value(node)}});
    {%- if field_logic.counter_incrsaturates(node) %}
    {{field_logic.get_field_combo_identifier(node, "incrsaturate")}} = ({{field_logic.get_storage_identifier(node)}} >= {{field_logic.get_counter_incrsaturate_value(node)}});
    if(next_c > {{field_logic.get_counter_incrsaturate_value(node)}}) begin
        next_c = {{field_logic.get_counter_incrsaturate_value(node)}};
        load_next_c = '1;
    end
    {%- endif %}
{%- endmacro %}


{% macro down_counter(field) -%}
    if({{field_logic.get_counter_decr_strobe(node)}}) begin // decrement
        {%- if field_logic.counter_decrsaturates(node) %}
        if(({{node.width+1}})'(next_c) < ({{field_logic.get_counter_decrvalue(node)}} + {{field_logic.get_counter_decrsaturate_value(node)}})) begin // down-counter saturated
            next_c = {{field_logic.get_counter_decrsaturate_value(node)}};
        end else begin
            next_c = next_c - {{field_logic.get_counter_decrvalue(node)}};
        end
        {%- else %}
        {{field_logic.get_field_combo_identifier(node, "underflow")}} = (next_c < ({{field_logic.get_counter_decrvalue(node)}}));
        next_c = next_c - {{field_logic.get_counter_decrvalue(node)}};
        {%- endif %}
        load_next_c = '1;
    {%- if not field_logic.counter_decrsaturates(node) %}
    end else begin
        {{field_logic.get_field_combo_identifier(node, "underflow")}} = '0;
    {%- endif %}
    end
    {{field_logic.get_field_combo_identifier(node, "decrthreshold")}} = ({{field_logic.get_storage_identifier(node)}} <= {{field_logic.get_counter_decrthreshold_value(node)}});
    {%- if field_logic.counter_decrsaturates(node) %}
    {{field_logic.get_field_combo_identifier(node, "decrsaturate")}} = ({{field_logic.get_storage_identifier(node)}} <= {{field_logic.get_counter_decrsaturate_value(node)}});
    if(next_c < {{field_logic.get_counter_decrsaturate_value(node)}}) begin
        next_c = {{field_logic.get_counter_decrsaturate_value(node)}};
        load_next_c = '1;
    end
    {%- endif %}
{%- endmacro %}
