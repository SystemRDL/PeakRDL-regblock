// AHB Transfer Types
//localparam [1:0] HTRANS_IDLE   = 2'b00;
//localparam [1:0] HTRANS_BUSY   = 2'b01;
localparam [1:0] HTRANS_NONSEQ = 2'b10;
localparam [1:0] HTRANS_SEQ    = 2'b11;

// AHB Response Types
localparam HRESP_OKAY  = 1'b0;
localparam HRESP_ERROR = 1'b1;

// Request
logic is_active;
logic [{{cpuif.addr_width-1}}:0] addr_captured;
{%- if cpuif.data_width_bytes > 1 %}
logic [{{clog2(cpuif.data_width_bytes)-1}}:0] addr_offset_captured;
{%- endif %}
logic write_captured;
logic [2:0] size_captured;

always {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        is_active <= '0;
        cpuif_req <= '0;
        cpuif_req_is_wr <= '0;
        cpuif_addr <= '0;
        cpuif_wr_data <= '0;
        cpuif_wr_biten <= '0;
        addr_captured <= '0;
        {%- if cpuif.data_width_bytes > 1 %}
        addr_offset_captured <= '0;
        {%- endif %}
        write_captured <= '0;
        size_captured <= '0;
    end else begin
        if(~is_active) begin
            // Address Phase: Detect new transfer and capture address/control
            if({{cpuif.signal("hsel")}} && ({{cpuif.signal("htrans")}} == HTRANS_NONSEQ || {{cpuif.signal("htrans")}} == HTRANS_SEQ)) begin
                is_active <= '1;
                // Capture word-aligned address for register selection
                {%- if cpuif.data_width_bytes == 1 %}
                addr_captured <= {{cpuif.signal("haddr")}}[{{cpuif.addr_width-1}}:0];
                {%- else %}
                addr_captured <= { {{-cpuif.signal("haddr")}}[{{cpuif.addr_width-1}}:{{clog2(cpuif.data_width_bytes)}}], {{clog2(cpuif.data_width_bytes)}}'b0};
                // Capture original address offset for byte enable calculation
                addr_offset_captured <= {{cpuif.signal("haddr")}}[0+:{{clog2(cpuif.data_width_bytes)}}];
                {%- endif %}
                write_captured <= {{cpuif.signal("hwrite")}};
                size_captured <= {{cpuif.signal("hsize")}};
            end
        end else begin
            // Data Phase: Start request with captured data
            cpuif_req <= '1;
            cpuif_req_is_wr <= write_captured;
            cpuif_addr <= addr_captured;

            // Replicate data based on captured HSIZE for proper lane placement
            case(size_captured)
                3'b000: begin // Byte access - replicate byte across all lanes
                    {%- if cpuif.data_width_bytes == 1 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:8];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//1}}{ {{cpuif.signal("hwdata")}}[0+:8] } };
                    {%- endif %}
                end
                {%- if cpuif.data_width_bytes >= 2 %}
                3'b001: begin // Halfword access - replicate halfword across all lanes
                    {%- if cpuif.data_width_bytes == 2 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:16];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//2}}{ {{cpuif.signal("hwdata")}}[0+:16] } };
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 4 %}
                3'b010: begin // Word access - replicate word across all lanes
                    {%- if cpuif.data_width_bytes == 4 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:32];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//4}}{ {{cpuif.signal("hwdata")}}[0+:32] } };
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 8 %}
                3'b011: begin // Doubleword access - replicate doubleword across all lanes
                    {%- if cpuif.data_width_bytes == 8 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:64];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//8}}{ {{cpuif.signal("hwdata")}}[0+:64] } };
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 16 %}
                3'b100: begin // 128-bit access - replicate 128-bit data across all lanes
                    {%- if cpuif.data_width_bytes == 16 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:128];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//16}}{ {{cpuif.signal("hwdata")}}[0+:128] } };
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 32 %}
                3'b101: begin // 256-bit access - replicate 256-bit data across all lanes
                    {%- if cpuif.data_width_bytes == 32 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:256];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//32}}{ {{cpuif.signal("hwdata")}}[0+:256] } };
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 64 %}
                3'b110: begin // 512-bit access - replicate 512-bit data across all lanes
                    {%- if cpuif.data_width_bytes == 64 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:512];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//64}}{ {{cpuif.signal("hwdata")}}[0+:512] } };
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 128 %}
                3'b111: begin // 1024-bit access - replicate 1024-bit data across all lanes
                    {%- if cpuif.data_width_bytes == 128 %}
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}}[0+:1024];
                    {%- else %}
                    cpuif_wr_data <= { {{cpuif.data_width_bytes//128}}{ {{cpuif.signal("hwdata")}}[0+:1024] } };
                    {%- endif %}
                end
                {%- endif %}
                default: begin // Larger than supported accesses (full width)
                    cpuif_wr_data <= {{cpuif.signal("hwdata")}};
                end
                endcase

            // Generate byte enable based on captured HSIZE and original address offset
            cpuif_wr_biten <= '0;
            case(size_captured)
                3'b000: begin // Byte access
                    {%- if cpuif.data_width_bytes == 1 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured*8 +: 8] <= '1;
                    {%- endif %}
                end
                {%- if cpuif.data_width_bytes >= 2 %}
                3'b001: begin // Halfword access
                    {%- if cpuif.data_width_bytes == 2 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:1]*16 +: 16] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 4 %}
                3'b010: begin // Word access
                    {%- if cpuif.data_width_bytes == 4 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:2]*32 +: 32] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 8 %}
                3'b011: begin // Doubleword access
                    {%- if cpuif.data_width_bytes == 8 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:3]*64 +: 64] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 16 %}
                3'b100: begin // 128-bit access
                    {%- if cpuif.data_width_bytes == 16 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:4]*128 +: 128] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 32 %}
                3'b101: begin // 256-bit access
                    {%- if cpuif.data_width_bytes == 32 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:5]*256 +: 256] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 64 %}
                3'b110: begin // 512-bit access
                    {%- if cpuif.data_width_bytes == 64 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:6]*512 +: 512] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                {%- if cpuif.data_width_bytes >= 128 %}
                3'b111: begin // 1024-bit access
                    {%- if cpuif.data_width_bytes == 128 %}
                    cpuif_wr_biten <= '1;
                    {%- else %}
                    cpuif_wr_biten[addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:7]*1024 +: 1024] <= '1;
                    {%- endif %}
                end
                {%- endif %}
                default: begin // Default to full width access
                    cpuif_wr_biten <= '1;
                end
            endcase

            // End transaction when acknowledged
            if(cpuif_rd_ack || cpuif_wr_ack) begin
                is_active <= '0;
                cpuif_req <= '0;
            end
        end
    end
end

// Response
logic [{{cpuif.data_width-1}}:0] read_data_extracted;

// Extract read data based on captured HSIZE and address offset
always @(*) begin
    case(size_captured)
        3'b000: begin // Byte access - extract specific byte
            {%- if cpuif.data_width_bytes == 1 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 8}}'d0, cpuif_rd_data[(addr_offset_captured*8)+:8] };
            {%- endif %}
        end
        {%- if cpuif.data_width_bytes >= 2 %}
        3'b001: begin // Halfword access - extract specific halfword
            {%- if cpuif.data_width_bytes == 2 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 16}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:1]*16)+:16] };
            {%- endif %}
        end
        {%- endif %}
        {%- if cpuif.data_width_bytes >= 4 %}
        3'b010: begin // Word access - extract specific word
            {%- if cpuif.data_width_bytes == 4 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 32}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:2]*32)+:32] };
            {%- endif %}
        end
        {%- endif %}
        {%- if cpuif.data_width_bytes >= 8 %}
        3'b011: begin // Doubleword access - extract specific doubleword
            {%- if cpuif.data_width_bytes == 8 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 64}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:3]*64)+:64] };
            {%- endif %}
        end
        {%- endif %}
        {%- if cpuif.data_width_bytes >= 16 %}
        3'b100: begin // 128-bit access - extract specific 128-bit data
            {%- if cpuif.data_width_bytes == 16 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 128}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:4]*128)+:128] };
            {%- endif %}
        end
        {%- endif %}
        {%- if cpuif.data_width_bytes >= 32 %}
        3'b101: begin // 256-bit access - extract specific 256-bit data
            {%- if cpuif.data_width_bytes == 32 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 256}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:5]*256)+:256] };
            {%- endif %}
        end
        {%- endif %}
        {%- if cpuif.data_width_bytes >= 64 %}
        3'b110: begin // 512-bit access - extract specific 512-bit data
            {%- if cpuif.data_width_bytes == 64 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 512}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:6]*512)+:512] };
            {%- endif %}
        end
        {%- endif %}
        {%- if cpuif.data_width_bytes >= 128 %}
        3'b111: begin // 1024-bit access - extract specific 1024-bit data
            {%- if cpuif.data_width_bytes == 128 %}
            read_data_extracted = cpuif_rd_data;
            {%- else %}
            read_data_extracted = { {{cpuif.data_width - 1024}}'d0, cpuif_rd_data[(addr_offset_captured[{{clog2(cpuif.data_width_bytes)-1}}:7]*1024)+:1024] };
            {%- endif %}
        end
        {%- endif %}
        default: begin // Full width access for larger sizes
            read_data_extracted = cpuif_rd_data;
        end
    endcase
end

assign {{cpuif.signal("hready")}} = (cpuif_rd_ack | cpuif_wr_ack | ~is_active);
assign {{cpuif.signal("hrdata")}} = read_data_extracted;
assign {{cpuif.signal("hresp")}} = (cpuif_rd_err | cpuif_wr_err) ? HRESP_ERROR : HRESP_OKAY;

