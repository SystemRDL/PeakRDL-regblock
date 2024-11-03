{%- macro logic_type(field) %}
    {%- if field.width == 1 -%}
std_logic
    {%- else -%}
std_logic_vector
    {%- endif %}
{%- endmacro -%}

{%- macro up_counter(field) -%}
    if {{field_logic.get_counter_incr_strobe(node)}} then -- increment
        {%- if field_logic.counter_incrsaturates(node) %}
        if (to_unsigned('0' & next_c) + to_unsigned({{field_logic.get_counter_incrvalue(node)}})) > to_unsigned({{field_logic.get_counter_incrsaturate_value(node)}}) then -- up-counter saturated
            next_c := {{field_logic.get_counter_incrsaturate_value(node)}};
        else
            next_c := to_{{ logic_type(field) }}(to_unsigned(next_c) + to_unsigned({{field_logic.get_counter_incrvalue(node)}}));
        end if;
        {%- else %}
        {{field_logic.get_field_combo_identifier(node, "overflow")}} <= to_std_logic((to_unsigned('0' & next_c) + to_unsigned({{field_logic.get_counter_incrvalue(node)}})) > to_unsigned({{get_value(2**node.width - 1, node.width)}}));
        next_c := to_{{ logic_type(field) }}(to_unsigned(next_c) + to_unsigned({{field_logic.get_counter_incrvalue(node)}}));
        {%- endif %}
        load_next_c := '1';
    {%- if not field_logic.counter_incrsaturates(node) %}
    else
        {{field_logic.get_field_combo_identifier(node, "overflow")}} <= '0';
    {%- endif %}
    end if;
    {{field_logic.get_field_combo_identifier(node, "incrthreshold")}} <= to_std_logic(unsigned({{field_logic.get_storage_identifier(node)}}) >= to_unsigned({{field_logic.get_counter_incrthreshold_value(node)}}));
    {%- if field_logic.counter_incrsaturates(node) %}
    {{field_logic.get_field_combo_identifier(node, "incrsaturate")}} <= to_std_logic(unsigned({{field_logic.get_storage_identifier(node)}}) >= to_unsigned({{field_logic.get_counter_incrsaturate_value(node)}}));
    if to_unsigned(next_c) > to_unsigned({{field_logic.get_counter_incrsaturate_value(node)}}) then
        next_c := {{field_logic.get_counter_incrsaturate_value(node)}};
        load_next_c := '1';
    end if;
    {%- endif %}
{%- endmacro %}


{% macro down_counter(field) -%}
    if {{field_logic.get_counter_decr_strobe(node)}} then -- decrement
        {%- if field_logic.counter_decrsaturates(node) %}
        if to_unsigned('0' & next_c) < to_unsigned({{field_logic.get_counter_decrvalue(node)}}) + to_unsigned({{field_logic.get_counter_decrsaturate_value(node)}}) then -- down-counter saturated
            next_c := {{field_logic.get_counter_decrsaturate_value(node)}};
        else
            next_c := to_{{ logic_type(field) }}(to_unsigned(next_c) - to_unsigned({{field_logic.get_counter_decrvalue(node)}}));
        end if;
        {%- else %}
        {{field_logic.get_field_combo_identifier(node, "underflow")}} <= to_std_logic(to_unsigned(next_c) < to_unsigned({{field_logic.get_counter_decrvalue(node)}}));
        next_c := to_{{ logic_type(field) }}(to_unsigned(next_c) - to_unsigned({{field_logic.get_counter_decrvalue(node)}}));
        {%- endif %}
        load_next_c := '1';
    {%- if not field_logic.counter_decrsaturates(node) %}
    else
        {{field_logic.get_field_combo_identifier(node, "underflow")}} <= '0';
    {%- endif %}
    end if;
    {{field_logic.get_field_combo_identifier(node, "decrthreshold")}} <= to_std_logic(unsigned({{field_logic.get_storage_identifier(node)}}) <= to_unsigned({{field_logic.get_counter_decrthreshold_value(node)}}));
    {%- if field_logic.counter_decrsaturates(node) %}
    {{field_logic.get_field_combo_identifier(node, "decrsaturate")}} <= to_std_logic(unsigned({{field_logic.get_storage_identifier(node)}}) <= to_unsigned({{field_logic.get_counter_decrsaturate_value(node)}}));
    if to_unsigned(next_c) < to_unsigned({{field_logic.get_counter_decrsaturate_value(node)}}) then
        next_c := {{field_logic.get_counter_decrsaturate_value(node)}};
        load_next_c := '1';
    end if;
    {%- endif %}
{%- endmacro %}
