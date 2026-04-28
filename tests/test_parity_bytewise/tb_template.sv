{% extends "lib/tb_base.sv" %}

{% block declarations %}
    logic [regblock_pkg::N_PARITY_FIELDS-1:0] field_parity_error;
    logic                                       error_clear_i = '0;
    logic [$clog2(regblock_pkg::N_PARITY_BITS)-1:0] parity_inject_sel = '0;
    logic                                       parity_inject_strobe = '0;
{% endblock %}

{% block clocking_dirs %}
        input  field_parity_error;
        output error_clear_i;
        output parity_inject_sel;
        output parity_inject_strobe;
{% endblock %}

{% block seq %}
    {% sv_line_anchor %}
    ##1;
    cb.rst <= '0;
    ##2;

    // -------------------------------------------------------------------------
    // 1) Reset baseline — no errors
    // -------------------------------------------------------------------------
    @cb;
    assert(field_parity_error == '0)
        else $error("Reset baseline: expected all zero, got %h", field_parity_error);

    // -------------------------------------------------------------------------
    // 2) SW write to multi-byte field; observe parity follows data
    // -------------------------------------------------------------------------
    cpuif.write('h0, 32'h7FF);  // mbr.f_11bit = 0x7FF
    @cb;
    assert(field_parity_error == '0)
        else $error("After SW write: unexpected parity error %h", field_parity_error);

    // -------------------------------------------------------------------------
    // 3) Inject at every parity bit. Each must set the corresponding sticky bit.
    // -------------------------------------------------------------------------
    for (int k = 0; k < regblock_pkg::N_PARITY_BITS; k++) begin
        cb.parity_inject_sel    <= k[$clog2(regblock_pkg::N_PARITY_BITS)-1:0];
        cb.parity_inject_strobe <= 1'b1;
        @cb;
        cb.parity_inject_strobe <= 1'b0;
        @cb;  // sticky latch
        assert(field_parity_error[regblock_pkg::PINJ_TO_FERR[k]] == 1'b1)
            else $error("Injection at bit %0d did not set field_parity_error[%0d]",
                        k, regblock_pkg::PINJ_TO_FERR[k]);
        // Clear before next iteration
        cb.error_clear_i <= 1'b1;
        @cb;
        cb.error_clear_i <= 1'b0;
        @cb;
        assert(field_parity_error == '0)
            else $error("After clear: residual error %h after injection at bit %0d",
                        field_parity_error, k);
    end

    // -------------------------------------------------------------------------
    // 4) SEU on stored data (force a bit) sets the field's sticky error.
    // -------------------------------------------------------------------------
    cpuif.write('h0, 32'h0);  // restore mbr = 0
    @cb;
    assert(field_parity_error == '0);

`ifdef XILINX_XSIM
    assign dut.field_storage.mbr.f_11bit.value[0] = 1'b1;
    deassign dut.field_storage.mbr.f_11bit.value[0];
`else
    force dut.field_storage.mbr.f_11bit.value[0] = 1'b1;
    release dut.field_storage.mbr.f_11bit.value[0];
`endif
    @cb;
    @cb;
    assert(field_parity_error[regblock_pkg::FERR_IDX_MBR_F_11BIT] == 1'b1)
        else $error("SEU on mbr.f_11bit not detected");

    // -------------------------------------------------------------------------
    // 4b) Parity is FROZEN between SW writes — a bit flip on stored data
    //     remains detected even after a long idle period.
    //
    //     mbr.f_11bit is sw=rw, hw=r (no HW write path), so the only way
    //     parity should ever change is via a SW write through load_next.
    //     If parity were instead recomputed from the live `value` every
    //     cycle, the comparator could never catch a bit flip.
    // -------------------------------------------------------------------------
    // Restore coherence and clear the sticky from step 4.
    cpuif.write('h0, 32'h0);
    @cb;
    cb.error_clear_i <= 1'b1;
    @cb;
    cb.error_clear_i <= 1'b0;
    @cb;
    assert(field_parity_error == '0);

    // Write a non-trivial pattern.
    //   mbr.f_11bit = 0x055 → parity[0] = ^8'h55 = 0, parity[1] = ^3'h0 = 0
    cpuif.write('h0, 32'h055);
    @cb;
    assert(field_parity_error == '0)
        else $error("After write 0x055, expected no error");

    // Hold for a long idle period with NO writes; the comparator must
    // continue to see value/parity coherent every cycle.
    repeat (20) @cb;
    assert(field_parity_error == '0)
        else $error("Idle hold: parity_error toggled without any data change");

    // Now force a bit flip on the stored value. Because the field has no
    // HW-write path AND no SW write occurs, no load_next pulse will fire.
    // Parity must NOT track the change. The comparator must catch it
    // immediately and the sticky must latch.
`ifdef XILINX_XSIM
    assign dut.field_storage.mbr.f_11bit.value[0] = 1'b0;
    deassign dut.field_storage.mbr.f_11bit.value[0];
`else
    force dut.field_storage.mbr.f_11bit.value[0] = 1'b0;
    release dut.field_storage.mbr.f_11bit.value[0];
`endif
    // Hold for a long idle period — parity stays frozen, so the mismatch
    // persists every cycle and the sticky bit must remain set.
    repeat (10) @cb;
    assert(field_parity_error[regblock_pkg::FERR_IDX_MBR_F_11BIT] == 1'b1)
        else $error("Frozen-parity check: SEU on f_11bit was silently absorbed (parity refreshing?)");

    // Restore good data via a SW write (force/release leaves the variable
    // in its forced state per SV LRM, so a SW write is needed to refresh
    // both value and parity together).
    cpuif.write('h0, 32'h0);
    @cb;
    @cb;
    // Now clear; the bit should clear and stay cleared because value/parity
    // are coherent again.
    cb.error_clear_i <= 1'b1;
    @cb;
    cb.error_clear_i <= 1'b0;
    @cb;
    assert(field_parity_error == '0)
        else $error("Sticky did not clear after data restored, field_parity_error=%b", field_parity_error);

{% endblock %}
