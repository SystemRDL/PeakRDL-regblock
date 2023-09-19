# AMD/Xilinx Vivado
# Source the settings script from default install path.
source /tools/Xilinx/Vivado/2023.1/settings64.sh

# Questa*-Intel® FPGA Starter Edition Software
# Add bin folder parth to PATH environment variable.
export PATH="$HOME/intelFPGA_pro/23.2/questa_fse/bin:$PATH"

# Specify path to license file.
# There is not default path here, every user should edit it.
export LM_LICENSE_FILE=$HOME/intelFPGA_pro/License.dat