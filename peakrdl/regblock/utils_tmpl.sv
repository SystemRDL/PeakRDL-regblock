
/*
 * Creates an always_ff begin/end block with the appropriate edge sensitivity
 * list depending on the resetsignal used
 */
{% macro AlwaysFF(resetsignal) %}
{%- if resetsignal.is_async and resetsignal.is_activehigh %}
always_ff @(posedge clk or posedge {{resetsignal.identifier}}) begin
{%- elif resetsignal.is_async and not resetsignal.is_activehigh %}
always_ff @(posedge clk or negedge {{resetsignal.identifier}}) begin
{%- else %}
always_ff @(posedge clk) begin
{%- endif %}
{{- caller() }}
end
{%- endmacro %}
