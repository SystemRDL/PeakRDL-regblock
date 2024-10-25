{% macro up_counter(field) -%}
    if {{field_logic.get_counter_incr_strobe(node)}} then -- increment
        {%- if field_logic.counter_incrsaturates(node) %}
        if (('0' & next_c) + {{field_logic.get_counter_incrvalue(node)}}) > {{field_logic.get_counter_incrsaturate_value(node)}} then -- up-counter saturated
            next_c := {{field_logic.get_counter_incrsaturate_value(node)}};
        else
            next_c := next_c + {{field_logic.get_counter_incrvalue(node)}};
        end if;
        {%- else %}
        {{field_logic.get_field_combo_identifier(node, "overflow")}} <= ((('0' & next_c) + {{field_logic.get_counter_incrvalue(node)}}) > {{get_value(2**node.width - 1, node.width)}});
        next_c := next_c + {{field_logic.get_counter_incrvalue(node)}};
        {%- endif %}
        load_next_c := '1';
    {%- if not field_logic.counter_incrsaturates(node) %}
    else
        {{field_logic.get_field_combo_identifier(node, "overflow")}} <= '0';
    {%- endif %}
    end if;
    {{field_logic.get_field_combo_identifier(node, "incrthreshold")}} <= ({{field_logic.get_storage_identifier(node)}} >= {{field_logic.get_counter_incrthreshold_value(node)}});
    {%- if field_logic.counter_incrsaturates(node) %}
    {{field_logic.get_field_combo_identifier(node, "incrsaturate")}} = ({{field_logic.get_storage_identifier(node)}} >= {{field_logic.get_counter_incrsaturate_value(node)}});
    if next_c > {{field_logic.get_counter_incrsaturate_value(node)}} then
        next_c := {{field_logic.get_counter_incrsaturate_value(node)}};
        load_next_c := '1';
    end
    {%- endif %}
{%- endmacro %}


{% macro down_counter(field) -%}
    if {{field_logic.get_counter_decr_strobe(node)}} then -- decrement
        {%- if field_logic.counter_decrsaturates(node) %}
        if ('0' & next_c) < ({{field_logic.get_counter_decrvalue(node)}} + {{field_logic.get_counter_decrsaturate_value(node)}}) then -- down-counter saturated
            next_c := {{field_logic.get_counter_decrsaturate_value(node)}};
        else
            next_c := next_c - {{field_logic.get_counter_decrvalue(node)}};
        end if;
        {%- else %}
        {{field_logic.get_field_combo_identifier(node, "underflow")}} <= (next_c < ({{field_logic.get_counter_decrvalue(node)}}));
        next_c := next_c - {{field_logic.get_counter_decrvalue(node)}};
        {%- endif %}
        load_next_c := '1';
    {%- if not field_logic.counter_decrsaturates(node) %}
    else
        {{field_logic.get_field_combo_identifier(node, "underflow")}} <= '0';
    {%- endif %}
    end if;
    {{field_logic.get_field_combo_identifier(node, "decrthreshold")}} <= ({{field_logic.get_storage_identifier(node)}} <= {{field_logic.get_counter_decrthreshold_value(node)}});
    {%- if field_logic.counter_decrsaturates(node) %}
    {{field_logic.get_field_combo_identifier(node, "decrsaturate")}} <= ({{field_logic.get_storage_identifier(node)}} <= {{field_logic.get_counter_decrsaturate_value(node)}});
    if next_c < {{field_logic.get_counter_decrsaturate_value(node)}} then
        next_c := {{field_logic.get_counter_decrsaturate_value(node)}};
        load_next_c := '1';
    end if;
    {%- endif %}
{%- endmacro %}
