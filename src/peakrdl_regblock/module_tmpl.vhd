-- Generated by PeakRDL-regblock - A free and open-source SystemVerilog generator
--  https://github.com/SystemRDL/PeakRDL-regblock

entity {{ds.module_name}} is
    {%- if cpuif.parameters %}
    generic (
        {{";\n        ".join(cpuif.parameters)}}
    );
    {%- endif %}
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

        {{cpuif.port_declaration|indent(8)}}
        {%- if hwif.has_input_struct or hwif.has_output_struct %};{% endif %}

        {{hwif.port_declaration|indent(8)}}
    );
end entity {{ds.module_name}};

architecture rtl of {{ds.module_name}} is
    ----------------------------------------------------------------------------
    -- CPU Bus interface signals
    ----------------------------------------------------------------------------
    signal cpuif_req : std_logic;
    signal cpuif_req_is_wr : std_logic;
    signal cpuif_addr : std_logic_vector({{cpuif.addr_width-1}} downto 0);
    signal cpuif_wr_data : std_logic_vector({{cpuif.data_width-1}} downto 0);
    signal cpuif_wr_biten : std_logic_vector({{cpuif.data_width-1}} downto 0);
    signal cpuif_req_stall_wr : std_logic;
    signal cpuif_req_stall_rd : std_logic;

    signal cpuif_rd_ack : std_logic;
    signal cpuif_rd_err : std_logic;
    signal cpuif_rd_data : std_logic_vector({{cpuif.data_width-1}} downto 0);

    signal cpuif_wr_ack : std_logic;
    signal cpuif_wr_err : std_logic;

    signal cpuif_req_masked : std_logic;

    {{cpuif.signal_declaration | indent}}

    {%- if ds.has_external_addressable %}
    signal external_req : std_logic;
    signal external_pending : std_logic;
    signal external_wr_ack : std_logic;
    signal external_rd_ack : std_logic;
    {%- endif %}
begin

    ----------------------------------------------------------------------------
    -- CPU Bus interface
    ----------------------------------------------------------------------------
    {{cpuif.get_implementation() | indent}}

{%- if ds.has_external_addressable %}
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            external_pending <= '0;
        end else begin
            if(external_req & ~external_wr_ack & ~external_rd_ack) external_pending <= '1;
            else if(external_wr_ack | external_rd_ack) external_pending <= '0;
            assert(!external_wr_ack || (external_pending | external_req))
                else $error("An external wr_ack strobe was asserted when no external request was active");
            assert(!external_rd_ack || (external_pending | external_req))
                else $error("An external rd_ack strobe was asserted when no external request was active");
        end
    end
{%- endif %}
{% if ds.min_read_latency == ds.min_write_latency %}
    -- Read & write latencies are balanced. Stalls not required
    {%- if ds.has_external_addressable %}
    -- except if external
    assign cpuif_req_stall_rd = external_pending;
    assign cpuif_req_stall_wr = external_pending;
    {%- else %}
    assign cpuif_req_stall_rd = '0;
    assign cpuif_req_stall_wr = '0;
    {%- endif %}
{%- elif ds.min_read_latency > ds.min_write_latency %}
    -- Read latency > write latency. May need to delay next write that follows a read
    logic [{{ds.min_read_latency - ds.min_write_latency - 1}}:0] cpuif_req_stall_sr;
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            cpuif_req_stall_sr <= '0;
        end else if(cpuif_req && !cpuif_req_is_wr) begin
            cpuif_req_stall_sr <= '1;
        end else begin
            cpuif_req_stall_sr <= (cpuif_req_stall_sr >> 'd1);
        end
    end
    {%- if ds.has_external_addressable %}
    assign cpuif_req_stall_rd = external_pending;
    assign cpuif_req_stall_wr = cpuif_req_stall_sr[0] | external_pending;
    {%- else %}
    assign cpuif_req_stall_rd = '0;
    assign cpuif_req_stall_wr = cpuif_req_stall_sr[0];
    {%- endif %}
{%- else %}
    -- Write latency > read latency. May need to delay next read that follows a write
    logic [{{ds.min_write_latency - ds.min_read_latency - 1}}:0] cpuif_req_stall_sr;
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            cpuif_req_stall_sr <= '0;
        end else if(cpuif_req && cpuif_req_is_wr) begin
            cpuif_req_stall_sr <= '1;
        end else begin
            cpuif_req_stall_sr <= (cpuif_req_stall_sr >> 'd1);
        end
    end
    {%- if ds.has_external_addressable %}
    assign cpuif_req_stall_rd = cpuif_req_stall_sr[0] | external_pending;
    assign cpuif_req_stall_wr = external_pending;
    {%- else %}
    assign cpuif_req_stall_rd = cpuif_req_stall_sr[0];
    assign cpuif_req_stall_wr = '0;
    {%- endif %}
{%- endif %}
    assign cpuif_req_masked = cpuif_req
                            & !(!cpuif_req_is_wr & cpuif_req_stall_rd)
                            & !(cpuif_req_is_wr & cpuif_req_stall_wr);

    ----------------------------------------------------------------------------
    -- Address Decode
    ----------------------------------------------------------------------------
    {{address_decode.get_strobe_struct()|indent}}
    decoded_reg_strb_t decoded_reg_strb;
{%- if ds.has_external_addressable %}
    logic decoded_strb_is_external;
{% endif %}
{%- if ds.has_external_block %}
    logic [{{cpuif.addr_width-1}}:0] decoded_addr;
{% endif %}
    logic decoded_req;
    logic decoded_req_is_wr;
    logic [{{cpuif.data_width-1}}:0] decoded_wr_data;
    logic [{{cpuif.data_width-1}}:0] decoded_wr_biten;

    always_comb begin
    {%- if ds.has_external_addressable %}
        automatic logic is_external;
        is_external = '0;
    {%- endif %}
        {{address_decode.get_implementation()|indent(8)}}
    {%- if ds.has_external_addressable %}
        decoded_strb_is_external = is_external;
        external_req = is_external;
    {%- endif %}
    end

    -- Pass down signals to next stage
{%- if ds.has_external_block %}
    assign decoded_addr = cpuif_addr;
{% endif %}
    assign decoded_req = cpuif_req_masked;
    assign decoded_req_is_wr = cpuif_req_is_wr;
    assign decoded_wr_data = cpuif_wr_data;
    assign decoded_wr_biten = cpuif_wr_biten;
{% if ds.has_writable_msb0_fields %}
    -- bitswap for use by fields with msb0 ordering
    logic [{{cpuif.data_width-1}}:0] decoded_wr_data_bswap;
    logic [{{cpuif.data_width-1}}:0] decoded_wr_biten_bswap;
    assign decoded_wr_data_bswap = {<<{decoded_wr_data}};
    assign decoded_wr_biten_bswap = {<<{decoded_wr_biten}};
{%- endif %}

{%- if ds.has_buffered_write_regs %}

    ----------------------------------------------------------------------------
    -- Write double-buffers
    ----------------------------------------------------------------------------
    {{write_buffering.get_storage_struct()|indent}}

    {{write_buffering.get_implementation()|indent}}
{%- endif %}
    ----------------------------------------------------------------------------
    -- Field logic
    ----------------------------------------------------------------------------
    {{field_logic.get_combo_struct()|indent}}

    {{field_logic.get_storage_struct()|indent}}

    {{field_logic.get_implementation()|indent}}

{%- if ds.has_paritycheck %}

    ----------------------------------------------------------------------------
    -- Parity Error
    ----------------------------------------------------------------------------
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            parity_error <= '0;
        end else begin
            automatic logic err;
            err = '0;
            {{parity.get_implementation()|indent(12)}}
            parity_error <= err;
        end
    end
{%- endif %}

{%- if ds.has_buffered_read_regs %}

    ----------------------------------------------------------------------------
    -- Read double-buffers
    ----------------------------------------------------------------------------
    {{read_buffering.get_storage_struct()|indent}}

    {{read_buffering.get_implementation()|indent}}
{%- endif %}

    ----------------------------------------------------------------------------
    -- Write response
    ----------------------------------------------------------------------------
{%- if ds.has_external_addressable %}
    always_comb begin
        automatic logic wr_ack;
        wr_ack = '0;
        {{ext_write_acks.get_implementation()|indent(8)}}
        external_wr_ack = wr_ack;
    end
    assign cpuif_wr_ack = external_wr_ack | (decoded_req & decoded_req_is_wr & ~decoded_strb_is_external);
{%- else %}
    assign cpuif_wr_ack = decoded_req & decoded_req_is_wr;
{%- endif %}
    -- Writes are always granted with no error response
    assign cpuif_wr_err = '0;

    ----------------------------------------------------------------------------
    -- Readback
    ----------------------------------------------------------------------------
{%- if ds.has_external_addressable %}
    logic readback_external_rd_ack_c;
    always_comb begin
        automatic logic rd_ack;
        rd_ack = '0;
        {{ext_read_acks.get_implementation()|indent(8)}}
        readback_external_rd_ack_c = rd_ack;
    end

    logic readback_external_rd_ack;
    {%- if ds.retime_read_fanin %}
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            readback_external_rd_ack <= '0;
        end else begin
            readback_external_rd_ack <= readback_external_rd_ack_c;
        end
    end

    {%- else %}

    assign readback_external_rd_ack = readback_external_rd_ack_c;
    {%- endif %}
{%- endif %}

    logic readback_err;
    logic readback_done;
    logic [{{cpuif.data_width-1}}:0] readback_data;
{{readback_implementation|indent}}
{% if ds.retime_read_response %}
    always_ff {{get_always_ff_event(cpuif.reset)}} begin
        if({{get_resetsignal(cpuif.reset)}}) begin
            cpuif_rd_ack <= '0;
            cpuif_rd_data <= '0;
            cpuif_rd_err <= '0;
        {%- if ds.has_external_addressable %}
            external_rd_ack <= '0;
        {%- endif %}
        end else begin
        {%- if ds.has_external_addressable %}
            external_rd_ack <= readback_external_rd_ack;
            cpuif_rd_ack <= readback_done | readback_external_rd_ack;
        {%- else %}
            cpuif_rd_ack <= readback_done;
        {%- endif %}
            cpuif_rd_data <= readback_data;
            cpuif_rd_err <= readback_err;
        end
    end
{% else %}
    {%- if ds.has_external_addressable %}
    assign external_rd_ack = readback_external_rd_ack;
    assign cpuif_rd_ack = readback_done | readback_external_rd_ack;
    {%- else %}
    assign cpuif_rd_ack = readback_done;
    {%- endif %}
    assign cpuif_rd_data = readback_data;
    assign cpuif_rd_err = readback_err;
{%- endif %}
end architecture rtl;
{# (eof newline anchor) #}