onerror {resume}
quietly WaveActivateNextPane {} 0
add wave -noupdate /tb/rst
add wave -noupdate /tb/clk
add wave -noupdate /tb/apb/PSEL
add wave -noupdate /tb/apb/PENABLE
add wave -noupdate /tb/apb/PWRITE
add wave -noupdate /tb/apb/PADDR
add wave -noupdate /tb/apb/PWDATA
add wave -noupdate /tb/apb/PRDATA
add wave -noupdate /tb/apb/PREADY
add wave -noupdate /tb/apb/PSLVERR
add wave -noupdate -divider DUT
add wave -noupdate /tb/dut/cpuif_req
add wave -noupdate /tb/dut/cpuif_req_is_wr
add wave -noupdate /tb/dut/cpuif_addr
add wave -noupdate /tb/dut/cpuif_wr_data
add wave -noupdate /tb/dut/cpuif_wr_bitstrb
add wave -noupdate /tb/dut/cpuif_rd_ack
add wave -noupdate /tb/dut/cpuif_rd_data
add wave -noupdate /tb/dut/cpuif_rd_err
add wave -noupdate /tb/dut/cpuif_wr_ack
add wave -noupdate /tb/dut/cpuif_wr_err
add wave -noupdate -divider Storage
add wave -noupdate -radix hexadecimal -childformat {{/tb/dut/field_storage.r0 -radix hexadecimal -childformat {{/tb/dut/field_storage.r0.a -radix hexadecimal} {/tb/dut/field_storage.r0.b -radix hexadecimal} {/tb/dut/field_storage.r0.c -radix hexadecimal}}} {/tb/dut/field_storage.r1 -radix hexadecimal -childformat {{/tb/dut/field_storage.r1.a -radix hexadecimal} {/tb/dut/field_storage.r1.b -radix hexadecimal} {/tb/dut/field_storage.r1.c -radix hexadecimal}}} {/tb/dut/field_storage.r2 -radix hexadecimal -childformat {{/tb/dut/field_storage.r2.a -radix hexadecimal} {/tb/dut/field_storage.r2.b -radix hexadecimal} {/tb/dut/field_storage.r2.c -radix hexadecimal}}}} -expand -subitemconfig {/tb/dut/field_storage.r0 {-height 17 -radix hexadecimal -childformat {{/tb/dut/field_storage.r0.a -radix hexadecimal} {/tb/dut/field_storage.r0.b -radix hexadecimal} {/tb/dut/field_storage.r0.c -radix hexadecimal}} -expand} /tb/dut/field_storage.r0.a {-height 17 -radix hexadecimal} /tb/dut/field_storage.r0.b {-height 17 -radix hexadecimal} /tb/dut/field_storage.r0.c {-height 17 -radix hexadecimal} /tb/dut/field_storage.r1 {-height 17 -radix hexadecimal -childformat {{/tb/dut/field_storage.r1.a -radix hexadecimal} {/tb/dut/field_storage.r1.b -radix hexadecimal} {/tb/dut/field_storage.r1.c -radix hexadecimal}} -expand} /tb/dut/field_storage.r1.a {-height 17 -radix hexadecimal} /tb/dut/field_storage.r1.b {-height 17 -radix hexadecimal} /tb/dut/field_storage.r1.c {-height 17 -radix hexadecimal} /tb/dut/field_storage.r2 {-height 17 -radix hexadecimal -childformat {{/tb/dut/field_storage.r2.a -radix hexadecimal} {/tb/dut/field_storage.r2.b -radix hexadecimal} {/tb/dut/field_storage.r2.c -radix hexadecimal}} -expand} /tb/dut/field_storage.r2.a {-height 17 -radix hexadecimal} /tb/dut/field_storage.r2.b {-height 17 -radix hexadecimal} /tb/dut/field_storage.r2.c {-height 17 -radix hexadecimal}} /tb/dut/field_storage
add wave -noupdate -divider HWIF
add wave -noupdate -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.a -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.a.value -radix hexadecimal} {/tb/dut/hwif_out.r0.a.anded -radix hexadecimal}}} {/tb/dut/hwif_out.r0.b -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.b.value -radix hexadecimal} {/tb/dut/hwif_out.r0.b.ored -radix hexadecimal}}} {/tb/dut/hwif_out.r0.c -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.c.value -radix hexadecimal} {/tb/dut/hwif_out.r0.c.swmod -radix hexadecimal}}}}} {/tb/dut/hwif_out.r1 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r1.a -radix hexadecimal} {/tb/dut/hwif_out.r1.b -radix hexadecimal} {/tb/dut/hwif_out.r1.c -radix hexadecimal}}} {/tb/dut/hwif_out.r2 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r2.a -radix hexadecimal} {/tb/dut/hwif_out.r2.b -radix hexadecimal} {/tb/dut/hwif_out.r2.c -radix hexadecimal}}}} -expand -subitemconfig {/tb/dut/hwif_out.r0 {-height 17 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.a -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.a.value -radix hexadecimal} {/tb/dut/hwif_out.r0.a.anded -radix hexadecimal}}} {/tb/dut/hwif_out.r0.b -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.b.value -radix hexadecimal} {/tb/dut/hwif_out.r0.b.ored -radix hexadecimal}}} {/tb/dut/hwif_out.r0.c -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.c.value -radix hexadecimal} {/tb/dut/hwif_out.r0.c.swmod -radix hexadecimal}}}} -expand} /tb/dut/hwif_out.r0.a {-height 17 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.a.value -radix hexadecimal} {/tb/dut/hwif_out.r0.a.anded -radix hexadecimal}} -expand} /tb/dut/hwif_out.r0.a.value {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r0.a.anded {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r0.b {-height 17 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.b.value -radix hexadecimal} {/tb/dut/hwif_out.r0.b.ored -radix hexadecimal}} -expand} /tb/dut/hwif_out.r0.b.value {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r0.b.ored {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r0.c {-height 17 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r0.c.value -radix hexadecimal} {/tb/dut/hwif_out.r0.c.swmod -radix hexadecimal}} -expand} /tb/dut/hwif_out.r0.c.value {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r0.c.swmod {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r1 {-height 17 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r1.a -radix hexadecimal} {/tb/dut/hwif_out.r1.b -radix hexadecimal} {/tb/dut/hwif_out.r1.c -radix hexadecimal}} -expand} /tb/dut/hwif_out.r1.a {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r1.b {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r1.c {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r2 {-height 17 -radix hexadecimal -childformat {{/tb/dut/hwif_out.r2.a -radix hexadecimal} {/tb/dut/hwif_out.r2.b -radix hexadecimal} {/tb/dut/hwif_out.r2.c -radix hexadecimal}} -expand} /tb/dut/hwif_out.r2.a {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r2.b {-height 17 -radix hexadecimal} /tb/dut/hwif_out.r2.c {-height 17 -radix hexadecimal}} /tb/dut/hwif_out
TreeUpdate [SetDefaultTree]
WaveRestoreCursors {{Cursor 1} {650000 ps} 0}
quietly wave cursor active 1
configure wave -namecolwidth 150
configure wave -valuecolwidth 100
configure wave -justifyvalue left
configure wave -signalnamewidth 0
configure wave -snapdistance 10
configure wave -datasetprefix 0
configure wave -rowmargin 4
configure wave -childrowmargin 2
configure wave -gridoffset 0
configure wave -gridperiod 1
configure wave -griddelta 40
configure wave -timeline 0
configure wave -timelineunits ps
update
WaveRestoreZoom {252900 ps} {755184 ps}
