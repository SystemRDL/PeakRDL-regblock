set this_dir [file dirname [file normalize [info script]]]
set files $argv


# Multi-driven
set_msg_config -id {[Synth 8-6858]} -new_severity "ERROR"
set_msg_config -id {[Synth 8-6859]} -new_severity "ERROR"

# Implicit net
set_msg_config -id {[Synth 8-992]} -new_severity "ERROR"

# Non-combo always_comb
set_msg_config -id {[Synth 8-87]} -new_severity "ERROR"

# Latch
set_msg_config -id {[Synth 8-327]} -new_severity "ERROR"

# Timing loop
set_msg_config -id {[Synth 8-295]} -new_severity "ERROR"

# Promote all critical warnings to errors
set_msg_config -severity {CRITICAL WARNING} -new_severity "ERROR"


set_part [lindex [get_parts] 0]
read_verilog -sv $files
read_xdc $this_dir/constr.xdc
synth_design -top regblock -mode out_of_context

#write_checkpoint -force synth.dcp

if {[get_msg_config -count -severity {CRITICAL WARNING}] || [get_msg_config -count -severity ERROR]} {
    error "Encountered errors"
}
