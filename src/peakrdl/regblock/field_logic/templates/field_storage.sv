{%- import 'field_logic/templates/counter_macros.sv' as counter_macros with context -%}
// Field: {{node.get_path()}}
always_comb begin
    automatic logic [{{node.width-1}}:0] next_c = {{field_logic.get_storage_identifier(node)}};
    automatic logic load_next_c = '0;
    {%- for signal in extra_combo_signals %}
    {{field_logic.get_field_combo_identifier(node, signal.name)}} = {{signal.default_assignment}};
    {%- endfor %}
    {% for conditional in conditionals %}
    {%- if not loop.first %} else {% endif %}if({{conditional.get_predicate(node)}}) begin // {{conditional.comment}}
        {%- for assignment in conditional.get_assignments(node) %}
        {{assignment|indent}}
        {%- endfor %}
    end
    {%- endfor %}
    {%- if node.is_up_counter %}
    {{counter_macros.up_counter(node)}}
    {%- endif %}
    {%- if node.is_down_counter %}
    {{counter_macros.down_counter(node)}}
    {%- endif %}
    {{field_logic.get_field_combo_identifier(node, "next")}} = next_c;
    {{field_logic.get_field_combo_identifier(node, "load_next")}} = load_next_c;
end
always_ff {{get_always_ff_event(resetsignal)}} begin
    {% if reset is not none -%}
    if({{get_resetsignal(resetsignal)}}) begin
        {{field_logic.get_storage_identifier(node)}} <= {{reset}};
    end else {% endif %}if({{field_logic.get_field_combo_identifier(node, "load_next")}}) begin
        {{field_logic.get_storage_identifier(node)}} <= {{field_logic.get_field_combo_identifier(node, "next")}};
    end
    {%- if field_logic.has_next_q(node) %}
    {{field_logic.get_next_q_identifier(node)}} <= {{get_input_identifier(node)}};
    {%- endif %}
end
