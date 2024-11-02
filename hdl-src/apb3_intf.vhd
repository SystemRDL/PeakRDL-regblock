library ieee;
context ieee.ieee_std_context;

package apb3_intf_pkg is

    type apb3_slave_in_intf is record
        PSEL : std_logic;
        PENABLE : std_logic;
        PWRITE : std_logic;
        PADDR : std_logic_vector;
        PWDATA : std_logic_vector;
    end record apb3_slave_in_intf;

    type apb3_slave_out_intf is record
        PRDATA : std_logic_vector;
        PREADY : std_logic;
        PSLVERR : std_logic;
    end record apb3_slave_out_intf;

end package apb3_intf_pkg;

-- package body apb3_intf_pkg is
-- end package body apb3_intf_pkg;
