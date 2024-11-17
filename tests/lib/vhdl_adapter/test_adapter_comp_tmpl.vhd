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

package regblock_adapter_vhdl_comp is

    component regblock_adapter_vhdl is
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
    end component regblock_adapter_vhdl;

end package regblock_adapter_vhdl_comp;