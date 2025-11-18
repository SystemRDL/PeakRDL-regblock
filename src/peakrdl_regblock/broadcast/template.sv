{#
    Template for generating broadcast write logic.

    For each broadcaster, this generates signals that combine the broadcaster's
    address strobe with the write direction qualifier.

    Context variables:
    - broadcaster_list: List of broadcaster info dicts with 'node', 'path', 'targets'
    - dereferencer: Dereferencer instance
#}
//-----------------------------------------------------------------------------
// Broadcast Write Logic
//-----------------------------------------------------------------------------
// Broadcasters write to multiple target registers simultaneously
// The broadcaster itself has no storage

{%- for broadcaster_info in broadcaster_list %}

// Broadcaster: {{broadcaster_info.path}}
// Targets: {{broadcaster_info.targets|length}} register(s)
{%- set broadcaster = broadcaster_info.node %}
{%- if broadcaster.is_array %}
{%- for idx_list in get_array_iterators(broadcaster) %}
wire broadcast_wr_{{get_signal_name(broadcaster, idx_list)}} = {{get_access_strobe(broadcaster, idx_list)}} && decoded_req_is_wr;
{%- endfor %}
{%- else %}
wire broadcast_wr_{{get_signal_name(broadcaster, None)}} = {{get_access_strobe(broadcaster, None)}} && decoded_req_is_wr;
{%- endif %}

{%- endfor %}
