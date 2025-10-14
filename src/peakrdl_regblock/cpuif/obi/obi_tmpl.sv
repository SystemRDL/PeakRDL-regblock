{%- if cpuif.is_interface -%}
`ifndef SYNTHESIS
    initial begin
        assert_bad_addr_width: assert($bits({{cpuif.signal("addr")}}) >= {{ds.package_name}}::{{ds.module_name.upper()}}_MIN_ADDR_WIDTH)
            else $error("Interface address width of %0d is too small. Shall be at least %0d bits", $bits({{cpuif.signal("addr")}}), {{ds.package_name}}::{{ds.module_name.upper()}}_MIN_ADDR_WIDTH);
        assert_bad_data_width: assert($bits({{cpuif.signal("wdata")}}) == {{ds.package_name}}::{{ds.module_name.upper()}}_DATA_WIDTH)
            else $error("Interface data width of %0d is incorrect. Shall be %0d bits", $bits({{cpuif.signal("wdata")}}), {{ds.package_name}}::{{ds.module_name.upper()}}_DATA_WIDTH);
    end
`endif

{% endif -%}

// State & holding regs
logic is_active; // A request is being served (not yet fully responded)
logic gnt_q; // one-cycle grant for A-channel
logic rsp_pending; // response ready but not yet accepted by manager
logic [{{cpuif.data_width-1}}:0] rsp_rdata_q;
logic rsp_err_q;
logic [$bits({{cpuif.signal("rid")}})-1:0] rid_q;

// Latch AID on accept to echo back the response
always_ff {{get_always_ff_event(cpuif.reset)}} begin
    if ({{get_resetsignal(cpuif.reset)}}) begin
        is_active <= 1'b0;
        gnt_q <= 1'b0;
        rsp_pending <= 1'b0;
        rsp_rdata_q <= '0;
        rsp_err_q <= 1'b0;
        rid_q <= '0;

        cpuif_req <= '0;
        cpuif_req_is_wr <= '0;
        cpuif_addr <= '0;
        cpuif_wr_data <= '0;
        cpuif_wr_biten <= '0;
    end else begin
        // defaults
        cpuif_req <= 1'b0;
        gnt_q <= {{cpuif.signal("req")}} & ~is_active;

        // Accept new request when idle
        if (~is_active) begin
            if ({{cpuif.signal("req")}}) begin
                is_active <= 1'b1;
                cpuif_req <= 1'b1;
                cpuif_req_is_wr <= {{cpuif.signal("we")}};
                cpuif_addr <= {{cpuif.signal("addr")}};
                cpuif_wr_data <= {{cpuif.signal("wdata")}};
                rid_q <= {{cpuif.signal("aid")}};
                for (int i = 0; i < {{cpuif.data_width_bytes}}; i++) begin
                    cpuif_wr_biten[i*8 +: 8] <= {8{ {{cpuif.signal("be")}}[i] }};
                end
            end
        end

        // Capture response
        if (is_active && (cpuif_rd_ack || cpuif_wr_ack)) begin
            rsp_pending <= 1'b1;
            rsp_rdata_q <= cpuif_rd_data;
            rsp_err_q <= cpuif_rd_err | cpuif_wr_err;
            // NOTE: Keep 'is_active' asserted until the external R handshake completes
        end

        // Complete external R-channel handshake only if manager ready
        if (rsp_pending && {{cpuif.signal("rvalid")}} && {{cpuif.signal("rready")}}) begin
            rsp_pending <= 1'b0;
            is_active <= 1'b0; // free to accept the next request
        end
    end
end

// R-channel outputs (held stable while rsp_pending=1)
assign {{cpuif.signal("rvalid")}} = rsp_pending;
assign {{cpuif.signal("rdata")}} = rsp_rdata_q;
assign {{cpuif.signal("err")}} = rsp_err_q;
assign {{cpuif.signal("rid")}} = rid_q;

// A-channel grant (registered one-cycle pulse when we accept a request)
assign {{cpuif.signal("gnt")}} = gnt_q;
