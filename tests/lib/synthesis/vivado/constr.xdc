
create_clock -period 10.000 -name clk [get_ports clk]

set_input_delay -clock [get_clocks clk] -min -add_delay 0.000 [get_ports -filter {(DIRECTION == IN) && (NAME != clk)}]
set_input_delay -clock [get_clocks clk] -max -add_delay 0.000 [get_ports -filter {(DIRECTION == IN) && (NAME != clk)}]

set_output_delay -clock [get_clocks clk] -min -add_delay 0.000 [get_ports -filter {DIRECTION == OUT}]
set_output_delay -clock [get_clocks clk] -max -add_delay 0.000 [get_ports -filter {DIRECTION == OUT}]
