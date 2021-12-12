{% macro up_counter(field) -%}
    if({{field_logic.get_counter_incr_strobe(node)}}) begin // increment
        {%- if field_logic.counter_incrsaturates(node) %}
        if((({{node.width+1}})'(next_c) + {{field_logic.get_counter_incrvalue(node)}}) > {{field_logic.get_counter_incrsaturate_value(node)}}) begin // up-counter saturated
            next_c = {{field_logic.get_counter_incrsaturate_value(node)}};
        end else begin
            next_c = next_c + {{field_logic.get_counter_incrvalue(node)}};
        end
        {%- else %}
        field_combo.{{field_path}}.overflow = ((({{node.width+1}})'(next_c) + {{field_logic.get_counter_incrvalue(node)}}) > {{get_value(2**node.width - 1)}});
        next_c = next_c + {{field_logic.get_counter_incrvalue(node)}};
        {%- endif %}
        load_next_c = '1;
    {%- if not field_logic.counter_incrsaturates(node) %}
    end else begin
        field_combo.{{field_path}}.overflow = '0;
    {%- endif %}
    end
    field_combo.{{field_path}}.incrthreshold = (field_storage.{{field_path}} >= {{field_logic.get_counter_incrthreshold_value(node)}});
    {%- if field_logic.counter_incrsaturates(node) %}
    field_combo.{{field_path}}.incrsaturate = (field_storage.{{field_path}} >= {{field_logic.get_counter_incrsaturate_value(node)}});
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
        field_combo.{{field_path}}.underflow = (next_c < ({{field_logic.get_counter_decrvalue(node)}}));
        next_c = next_c - {{field_logic.get_counter_decrvalue(node)}};
        {%- endif %}
        load_next_c = '1;
    {%- if not field_logic.counter_decrsaturates(node) %}
    end else begin
        field_combo.{{field_path}}.underflow = '0;
    {%- endif %}
    end
    field_combo.{{field_path}}.decrthreshold = (field_storage.{{field_path}} <= {{field_logic.get_counter_decrthreshold_value(node)}});
    {%- if field_logic.counter_decrsaturates(node) %}
    field_combo.{{field_path}}.decrsaturate = (field_storage.{{field_path}} <= {{field_logic.get_counter_decrsaturate_value(node)}});
    if(next_c < {{field_logic.get_counter_decrsaturate_value(node)}}) begin
        next_c = {{field_logic.get_counter_decrsaturate_value(node)}};
        load_next_c = '1;
    end
    {%- endif %}
{%- endmacro %}
