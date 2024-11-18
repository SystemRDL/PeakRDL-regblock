module regblock_adapter_sv
    {%- if cpuif.parameters %} #(
        {{",\n        ".join(cpuif.parameters)}}
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

        {{cpuif.port_declaration|indent(8)}}
        {%- if hwif.has_input_struct or hwif.has_output_struct %},{% endif %}

        {{hwif.port_declaration|indent(8)}}
    );

    regblock_adapter_vhdl adpt_vhdl (
        .clk(clk),
        .{{default_resetsignal_name}}({{default_resetsignal_name}}),

        {%- for cpuif_sig in cpuif_signals %}
        .{{ (cpuif_sv_prefix + cpuif_sig[0]).replace(".", "_") }}({{ cpuif_sv_prefix + cpuif_sig[0] }}),
        {%- endfor %}

        {%- for hwif_sig, _ in hwif_signals %}
        .\{{ hwif_sig }} ({{ hwif_sig }})
        {%- if not loop.last %},{% endif -%}
        {%- endfor %}
    );

endmodule