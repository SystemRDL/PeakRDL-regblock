{%- macro escape(identifier) -%}
{%- if "." in identifier %}\{{identifier}} {% else %}{{identifier}}{% endif -%}
{%- endmacro -%}

module regblock_adapter_sv
    {%- if sv_cpuif.parameters %} #(
        {{",\n        ".join(sv_cpuif.parameters)}}
    ) {%- endif %} (
        input wire clk,
        input wire {{default_resetsignal_name}},

        {%- for signal in ds.out_of_hier_signals.values() %}
        {%- if signal.width == 1 %}
        input wire {{kwf(signal.inst_name)}},
        {%- else %}
        input wire [{{signal.width-1}}:0] {{kwf(signal.inst_name)}},
        {%- endif %}
        {%- endfor %}

        {%- if ds.has_paritycheck %}

        output logic parity_error,
        {%- endif %}

        {{sv_cpuif.port_declaration|indent(8)}}
        {%- if hwif.has_input_struct or hwif.has_output_struct %},{% endif %}

        {{hwif.port_declaration|indent(8)}}
    );

    regblock_adapter_vhdl adpt_vhdl (
        .clk(clk),
        .{{default_resetsignal_name}}({{default_resetsignal_name}}),

        {%- for cpuif_sig, _ in cpuif_signals %}
        .{{ escape(sv_cpuif.signal(cpuif_sig)) }}({{ sv_cpuif.signal(cpuif_sig) }}),
        {%- endfor %}

        {%- for hwif_sig, _ in hwif_signals %}
        .{{ escape(hwif_sig) }}({{ hwif_sig }})
        {%- if not loop.last %},{% endif -%}
        {%- endfor %}
    );

endmodule