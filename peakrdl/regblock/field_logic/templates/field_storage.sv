// Field: {{node.get_path()}}
always_comb begin
    field_combo.{{field_path}}.next = field_storage.{{field_path}};
    field_combo.{{field_path}}.load_next = '0;
    {%- for signal in extra_combo_signals %}
    field_combo.{{field_path}}.{{signal.name}} = {{signal.default_assignment}};
    {%- endfor %}
    {% for conditional in conditionals %}
    {%- if not loop.first %} else {% endif %}if({{conditional.get_predicate(node)}}) begin // {{conditional.comment}}
        {%- for assignment in conditional.get_assignments(node) %}
        {{assignment|indent}}
        {%- endfor %}
    end
    {%- endfor %}
end
always_ff {{get_always_ff_event(resetsignal)}} begin
    {% if resetsignal is not none -%}
    if({{resetsignal.activehigh_identifier}}) begin
        field_storage.{{field_path}} <= {{reset}};
    end else {% endif %}if(field_combo.{{field_path}}.load_next) begin
        field_storage.{{field_path}} <= field_combo.{{field_path}}.next;
    end
end
