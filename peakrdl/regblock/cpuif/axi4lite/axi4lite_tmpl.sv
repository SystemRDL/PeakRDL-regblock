enum logic [1:0] {
    CPUIF_IDLE,
    CPUIF_BRESP,
    CPUIF_RRESP
} cpuif_state;

logic cpuif_prev_was_rd;
always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if({{get_resetsignal(cpuif.reset)}}) begin
        cpuif_state <= CPUIF_IDLE;
        cpuif_prev_was_rd <= '0;

        cpuif_req <= '0;
        cpuif_req_is_wr <= '0;
        cpuif_addr <= '0;
        cpuif_wr_data <= '0;

        {{cpuif.signal("arready")}} <= '0;
        {{cpuif.signal("awready")}} <= '0;
        {{cpuif.signal("wready")}} <= '0;
        {{cpuif.signal("bvalid")}} <= '0;
        {{cpuif.signal("bresp")}} <= '0;
        {{cpuif.signal("rvalid")}} <= '0;
        {{cpuif.signal("rdata")}} <= '0;
        {{cpuif.signal("rresp")}} <= '0;
    end else begin
        // Load response transfers as they arrive
        if(cpuif_rd_ack) begin
            {{cpuif.signal("rvalid")}} <= '1;
            {{cpuif.signal("rdata")}} <= cpuif_rd_data;
            if(cpuif_rd_err) {{cpuif.signal("rresp")}} <= 2'b10; // SLVERR
            else {{cpuif.signal("rresp")}} <= 2'b00; // OKAY
        end
        if(cpuif_wr_ack) begin
            {{cpuif.signal("bvalid")}} <= '1;
            if(cpuif_wr_err) {{cpuif.signal("bresp")}} <= 2'b10; // SLVERR
            else {{cpuif.signal("bresp")}} <= 2'b00; // OKAY
        end

        // Transaction state machine
        case(cpuif_state)
            CPUIF_IDLE: begin
                // round-robin arbitrate between read/write requests
                // Allow read if previous transfer was not a read, or no write is active
                if({{cpuif.signal("arvalid")}} && (!cpuif_prev_was_rd || !{{cpuif.signal("awvalid")}} || !{{cpuif.signal("wvalid")}})) begin
                    cpuif_req <= '1;
                    cpuif_req_is_wr <= '0;
                    {%- if cpuif.data_width == 8 %}
                    cpuif_addr <= {{cpuif.signal("araddr")}}[{{cpuif.addr_width-1}}:0];
                    {%- else %}
                    cpuif_addr <= { {{-cpuif.signal("araddr")}}[{{cpuif.addr_width-1}}:{{clog2(cpuif.data_width_bytes)}}], {{clog2(cpuif.data_width_bytes)}}'b0};
                    {%- endif %}
                    {{cpuif.signal("arready")}} <= '1;
                    cpuif_state <= CPUIF_RRESP;
                end else if({{cpuif.signal("awvalid")}} && {{cpuif.signal("wvalid")}}) begin
                    {{cpuif.signal("awready")}} <= '1;
                    {{cpuif.signal("wready")}} <= '1;
                    if({{cpuif.signal("wstrb")}} != {{"%d'b" % cpuif.data_width_bytes}}{{"1" * cpuif.data_width_bytes}}) begin
                        // Unaligned writes or use of byte strobes is not supported yet
                        {{cpuif.signal("bvalid")}} <= '1;
                        {{cpuif.signal("bresp")}} <= 2'b10; // SLVERR
                    end else begin
                        cpuif_req <= '1;
                        cpuif_req_is_wr <= '1;
                        {%- if cpuif.data_width == 8 %}
                        cpuif_addr <= {{cpuif.signal("awaddr")}}[{{cpuif.addr_width-1}}:0];
                        {%- else %}
                        cpuif_addr <= { {{-cpuif.signal("awaddr")}}[{{cpuif.addr_width-1}}:{{clog2(cpuif.data_width_bytes)}}], {{clog2(cpuif.data_width_bytes)}}'b0};
                        {%- endif %}
                        cpuif_wr_data <= {{cpuif.signal("wdata")}};
                    end
                    cpuif_state <= CPUIF_BRESP;
                end
            end

            CPUIF_BRESP: begin
                cpuif_req <= '0;
                {{cpuif.signal("awready")}} <= '0;
                {{cpuif.signal("wready")}} <= '0;
                cpuif_prev_was_rd <= '0;
                if({{cpuif.signal("bvalid")}} && {{cpuif.signal("bready")}}) begin
                    {{cpuif.signal("bvalid")}} <= '0;
                    cpuif_state <= CPUIF_IDLE;
                end
            end

            CPUIF_RRESP: begin
                cpuif_req <= '0;
                {{cpuif.signal("arready")}} <= '0;
                cpuif_prev_was_rd <= '1;
                if({{cpuif.signal("rvalid")}} && {{cpuif.signal("rready")}}) begin
                    {{cpuif.signal("rvalid")}} <= '0;
                    cpuif_state <= CPUIF_IDLE;
                end
            end

            default: begin
                cpuif_state <= CPUIF_IDLE;
            end
        endcase
    end
end
