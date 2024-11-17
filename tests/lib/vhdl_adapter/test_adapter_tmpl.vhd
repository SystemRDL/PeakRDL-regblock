library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

{%- macro sig_type(width) %}
{%- if width == 1 -%}
std_logic
{%- else -%}
std_logic_vector({{width-1}} downto 0)
{%- endif %}
{%- endmacro %}

entity regblock_adapter_vhdl is
    port (
        clk : in std_logic;
        {{default_resetsignal_name}} : in std_logic;

        {%- for signal in ds.out_of_hier_signals.values() %}
        {%- if signal.width == 1 %}
        {{kwf(signal.inst_name)}} : in std_logic;
        {%- else %}
        {{kwf(signal.inst_name)}} : in std_logic_vector({{signal.width-1}} downto 0);
        {%- endif %}
        {%- endfor %}

        {%- if ds.has_paritycheck %}
        parity_error : out std_logic;
        {%- endif %}

        {%- for cpuif_sig, width in cpuif_signals_in %}
        {{ (cpuif_sv_prefix + cpuif_sig).replace(".", "__") }} : in {{ sig_type(width) }};
        {%- endfor %}
        {%- for cpuif_sig, width in cpuif_signals_out %}
        {{ (cpuif_sv_prefix + cpuif_sig).replace(".", "__") }} : out {{ sig_type(width) }};
        {%- endfor %}

        {%- for hwif_sig, width in hwif_signals %}
        {%- if hwif_sig.startswith("hwif_in") %}
        {{ hwif_sig.replace(".", "__").replace("][", "_").replace("]", "_").replace("[", "_") }} : in {{ sig_type(width) }}
        {%- else %}
        {{ hwif_sig.replace(".", "__").replace("][", "_").replace("]", "_").replace("[", "_") }} : out {{ sig_type(width) }}
        {%- endif %}
        {%- if not loop.last %};{% endif -%}
        {%- endfor %}
    );
end entity regblock_adapter_vhdl;

architecture rtl of regblock_adapter_vhdl is

begin

    dut: entity work.{{ds.module_name}}
        {%- if cpuif.parameters %}
        generic map (
            {%- for param in cpuif.parameters %}
            {{param}} => {{param}},
            {%- endfor %}
        )
        {%- endif %}
        port map (
            clk => clk,
            {{default_resetsignal_name}} => {{default_resetsignal_name}},

            {%- for signal in ds.out_of_hier_signals.values() %}
            {{kwf(signal.inst_name)}} => {{kwf(signal.inst_name)}},
            {%- endfor %}

            {%- if ds.has_paritycheck %}
            parity_error => parity_error,
            {%- endif %}

            {%- for cpuif_sig, _ in cpuif_signals_in %}
            {{ (cpuif_vhdl_in_prefix + cpuif_sig).replace(".", "__") }} => {{ (cpuif_sv_prefix + cpuif_sig).replace(".", "__") }},
            {%- endfor %}
            {%- for cpuif_sig, _ in cpuif_signals_out %}
            {{ (cpuif_vhdl_out_prefix + cpuif_sig).replace(".", "__") }} => {{ (cpuif_sv_prefix + cpuif_sig).replace(".", "__") }},
            {%- endfor %}

            {%- for hwif_sig, _ in hwif_signals %}
            {{ hwif_sig.replace("][", ", ").replace("[", "(").replace("]", ")") }} => {{ hwif_sig.replace(".", "__").replace("][", "_").replace("]", "_").replace("[", "_") }}
            {%- if not loop.last %},{% endif -%}
            {%- endfor %}
        );

end architecture;