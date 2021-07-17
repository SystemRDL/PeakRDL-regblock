// Field: {{node.get_path()}}
always_comb begin
    field_combo.{{field_path}}.next = '0;
    field_combo.{{field_path}}.load_next = '0;
    {%- for signal in extra_combo_signals %}
    field_combo.{{field_path}}.{{signal.name}} = {{signal.default_assignment}};
    {%- endfor %}
    {%- for conditional in conditionals %}
    {% if not loop.first %}end else {% endif %}if({{conditional.get_conditional(node)}}) begin
        {%- for assignment in conditional.get_assignments(node) %}
        {{assignment|indent}}
        {%- endfor %}
    end
    {%- endfor %}
end
always_ff {{get_always_ff_event(resetsignal)}} begin
    if({{resetsignal.activehigh_identifier}}) begin
        field_storage.{{field_path}} <= {{reset}};
    end else if(field_combo.{{field_path}}.load_next) begin
        field_storage.{{field_path}} <= field_combo.{{field_path}}.next;
    end
end
{% if has_value_output(node) -%}
    assign {{get_output_identifier(node)}} = field_storage.{{field_path}};
{%- endif -%}
