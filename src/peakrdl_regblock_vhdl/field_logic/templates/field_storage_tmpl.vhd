{%- import 'field_logic/templates/counter_macros_tmpl.vhd' as counter_macros with context %}
-- Field: {{node.get_path()}}
process(all)
    {%- if node.width == 1 %}
    variable next_c: std_logic;
    {%- else %}
    variable next_c: std_logic_vector({{node.width-1}} downto 0);
    {%- endif %}
    variable load_next_c: std_logic;
begin
    next_c := {{field_logic.get_storage_identifier(node)}};
    load_next_c := '0';

    {%- for signal in extra_combo_signals %}
    {{field_logic.get_field_combo_identifier(node, signal.name)}} <= {{signal.default_assignment}};
    {%- endfor %}
    {%- for conditional in conditionals %}
    {% if not loop.first %}els{% endif %}if {{conditional.get_predicate(node)}} then -- {{conditional.comment}}
        {%- for assignment in conditional.get_assignments(node) %}
        {{assignment|indent}}
        {%- endfor %}
    {%- endfor %}
{%- if unconditional %}
    {% if conditionals %}else -- {{unconditional.comment}}
        {%- for assignment in unconditional.get_assignments(node) %}
        {{assignment|indent}}
        {%- endfor %}
    end if;
    {%- else %}
    -- {{unconditional.comment}}
    {%- for assignment in unconditional.get_assignments(node) %}
    {{assignment|indent}}
    {%- endfor %}
    {%- endif %}
{%- else %}
    {%- if conditionals %}
    end if;
    {%- endif %}
{%- endif %}

    {%- if node.is_up_counter %}
    {{counter_macros.up_counter(node)}}
    {%- endif %}

    {%- if node.is_down_counter %}
    {{counter_macros.down_counter(node)}}
    {%- endif %}
    {{field_logic.get_field_combo_identifier(node, "next_q")}} <= next_c;
    {{field_logic.get_field_combo_identifier(node, "load_next")}} <= load_next_c;

    {%- if node.get_property('paritycheck') %}
    {{field_logic.get_parity_error_identifier(node)}} <= to_std_logic({{field_logic.get_parity_identifier(node)}} /= ({% if node.width != 1 %}xor {% endif %}{{field_logic.get_storage_identifier(node)}}));
    {%- endif %}
end process;

{%- macro field_set() %}
    {{field_logic.get_storage_identifier(node)}} <= {{field_logic.get_field_combo_identifier(node, "next_q")}};
    {%- if node.get_property('paritycheck') %}
    {{field_logic.get_parity_identifier(node)}} <= {% if node.width != 1 %}xor {% endif %}{{field_logic.get_field_combo_identifier(node, "next_q")}};
    {%- endif %}
{%- endmacro %}
process({{get_always_ff_event(resetsignal)}}) begin
    {%- if reset is not none %}
    {%- macro field_reset() %}
        {{field_logic.get_storage_identifier(node)}} <= {{reset}};
        {%- if node.get_property('paritycheck') %}
        {{field_logic.get_parity_identifier(node)}} <= {% if node.width != 1 %}xor std_logic_vector'{% endif %}({{reset}});
        {%- endif %}
    {%- endmacro %}
    if {{get_resetsignal(resetsignal, asynch=True)}} then -- async reset
        {{- field_reset() }}
    elsif rising_edge(clk) then
        if {{get_resetsignal(resetsignal, asynch=False)}} then -- sync reset
            {{- field_reset() | indent }}
        elsif {{field_logic.get_field_combo_identifier(node, "load_next")}} then
            {{- field_set() | indent(8) }}
        end if;
    end if;
    {%- else %}
    if rising_edge(clk) then
        if {{field_logic.get_field_combo_identifier(node, "load_next")}} then
            {{- field_set() | indent(8) }}
        end if;
    end if;
    {%- endif %}

    {%- if field_logic.has_next_q(node) %}
    {{field_logic.get_next_q_identifier(node)}} <= {{get_input_identifier(node)}};
    {%- endif %}
end process;
