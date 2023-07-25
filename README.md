# Caravel cocotb verification tutorial

This tutorial will show you how to use cocotb Caravel APIs in order to create a testbench which sets Caravel gpios to have a certain value. To do this, you first need to write the firmware which will run on the mangament SoC and you have to set the gpios mode to be management output and then monitor those gpios using python cocotb testbench and check them against the expected value.  

## The steps: 

### 1. Install prerequisites:
Make sure you followed the [quickstart guide](https://caravel-sim-infrastructure.readthedocs.io/en/latest/usage.html#quickstart-guide) to install the prerequisites and cloned the [Caravel cocotb simulation infrastructure repo](https://github.com/efabless/caravel-sim-infrastructure) 
### 2. Update design_info.yaml file:
Make sure you updated the paths inside the ``design_info.yaml`` to match your paths as shown [here](https://github.com/efabless/caravel-sim-infrastructure/tree/main/cocotb#update-design_infoyaml). You can find the file in the ```caravel-sim-infrastructure/cocotb/``` directory
### 3. Create the firmware program:
The firmware is written in C code and it is the program that will be running on the Caravel management SoC. You can use it to make any configurations you want. You can find a description for all the firmware C APIs [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/C_api.html#firmware-apis)
For example, you can use it to configure the GPIO pins to have a certain value as shown in the code below. You can find the source file [here](https://github.com/NouranAbdelaziz/caravel_user_project_cocotb_tutorial/blob/cocotb_dev/verilog/dv/cocotb/gpio_test/gpio_test.c):
```
#include <common.h> 
void main(){
  mgmt_gpio_o_enable();
  mgmt_gpio_wr(0);
  enable_hk_spi(0); 
  configure_all_gpios(GPIO_MODE_MGMT_STD_OUT);
  gpio_config_load();
  set_gpio_l(0x8F);
  mgmt_gpio_wr(1);
  return;
}
```
* ``#include <common.h>``  is used to include the firmware APIs. This must be included in any firmware that will use the APIs provided. 
* ``mgmt_gpio_o_enable();`` is a function used to set the management gpio to output (this is a single gpio pin inside used by the management soc). You can read more about this function [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/C_api.html#_CPPv418mgmt_gpio_o_enablev). 
* ``mgmt_gpio_wr(0);`` is a function to set the management gpio pin to a certain value. Here I am setting it to 0 and later will set it to 1 after the configurations are finished. This is to make sure in the python testbench that the configurations are done and you can begin to check the gpios value. You can read more about this function [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/C_api.html#_CPPv412mgmt_gpio_wrb). 
* ``enable_hk_spi(0);`` is used to disable housekeeping spi and this is required for gpio 3 to function as a normal gpio.  
* ``configure_all_gpios(GPIO_MODE_MGMT_STD_OUTPUT);`` is a function used to configure all caravel’s 38 gpio pins with a certain mode. Here I chose the ``GPIO_MODE_MGMT_STD_OUTPUT`` mode because I will use the gpios as output and the management SoC will be the one using the gpios not the user project. You can read more about this function [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/C_api.html#_CPPv419configure_all_gpios9gpio_mode). 
* ``gpio_config_load();`` is a function to load the gpios configuration. It must be called whenever we change gpio configuration. 
* ``set_gpio_l(0x8F);`` is a function used to set the value of the lower 32 gpios with a certain value. In this example the first 4 gpios and the 8th gpio will be set to 1 and the rest will be set to 0. you can read more about this function [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/C_api.html#_CPPv410set_gpio_lj). 
* ``mgmt_gpio_wr(1);`` is a function to set the management gpio to 1 to indicate configurations are done as explained above.

### 4. Create the python testbench:
The python testbench is used to monitor the signals of the Caravel chip just like the testbenches used in hardware simulators. You can find a description for all the python testbench APIs [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/python_api.html#python-apis). 
Continuing on the example above,  if we want to check whether the gpios are set to the correct value, we can do that using the following code. You can find the source file [here](https://github.com/NouranAbdelaziz/caravel_user_project_cocotb_tutorial/blob/cocotb_dev/verilog/dv/cocotb/gpio_test/gpio_test.py):

```
from cocotb_includes import * 
import cocotb

@cocotb.test() 
@report_test 
async def gpio_test(dut):
   caravelEnv = await test_configure(dut)
   await caravelEnv.release_csb()
   await caravelEnv.wait_mgmt_gpio(1)
   gpios_value_str = caravelEnv.monitor_gpio(37, 0).binstr
   cocotb.log.info (f"All gpios '{gpios_value_str}'")
   gpio_value_int = caravelEnv.monitor_gpio(37, 0).integer
   expected_gpio_value = 0xF8
   if (gpio_value_int == expected_gpio_value):
      cocotb.log.info (f"[TEST] Pass the gpio value is '{hex(gpio_value_int)}'")
   else:
      cocotb.log.error (f"[TEST] Fail the gpio value is :'{hex(gpio_value_int)}' expected {hex(expected_gpio_value)}")
```
* ``from cocotb_includes import *`` is to include the python APIs for Caravel. It must be included in any python testbench you create 
* ``import cocotb`` is to import cocotb library 
* ``@cocotb.test()`` is a function wrapper which must be used before any cocotb test. You can read more about it [here](https://docs.cocotb.org/en/stable/quickstart.html#creating-a-test)
* ``@report_test `` is a function wrapper which is used to configure the test reports
* ``async def gpio_test(dut):``  is to define the test function. The async keyword is the syntax used to define python coroutine function (a function which can run in the background and does need to complete executing in order to return to the caller function). You must name this function the same name you will give the test in the ``-test`` argument while running. Here for example I used ``gpio_test`` for both. 
* ``caravelEnv = await test_configure(dut)`` is used to set up what is needed for the caravel testing environment such as reset, clock, and timeout cycles.This function must be called before any test as it returns an object with type Cravel_env which has the functions we can use to monitor different Caravel signals.
* ``await caravelEnv.release_csb()`` is to release housekeeping spi. By default, the csb is gpio value is 1 in order to disable housekeeping spi. This function drives csb gpio pin to Z to enable using it as output.  
* ``await caravelEnv.wait_mgmt_gpio(1)`` is to wait until the management gpio is 1 to ensure that all the configurations done in the firmware are finished. The ``await`` keyword is used to stop the execution of the coroutine until it returns the results. You can read more about the function [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/python_api.html#interfaces.caravel.Caravel_env.wait_mgmt_gpio)
* ``gpios_value_str = caravelEnv.monitor_gpio(37, 0).binstr`` is used to get the value of the gpios. The monitor_gpio() function takes the gpio number or range as a tuple and returns a [BinaryValue](https://docs.cocotb.org/en/stable/library_reference.html#cocotb.binary.BinaryValue) object. You can read more about the function [here](https://caravel-sim-infrastructure.readthedocs.io/en/latest/python_api.html#interfaces.caravel.Caravel_env.monitor_gpio). One of the functions   of the BinaryValue object is binstr which returns the binary value as a string (string consists of 0s and 1s)
* ``cocotb.log.info (f"All gpios '{gpios_value_str}'")``will print the given string to the full.log file which can be useful to check what went wrong if the test fails
* ``gpio_value_int = caravelEnv.monitor_gpio(37, 0).integer`` will return the value of the gpios as an integer
* ``` 
  if (gpio_value_int == expected_gpio_value):
      cocotb.log.info (f"[TEST] Pass the gpio value is '{gpio_value_int}'")
   else:
      cocotb.log.error (f"[TEST] Fail the gpio value is :'{gpio_value_int}' expected {expected_gpio_value}")
   ```
   This compares the gpio value with the expected value and print a string to the log file if they are equal and raises an error if they are not equal. 

### 5. Place the test files in the user project:
Create a folder called gpio_test in ``<caravel_user_project>/verilog/dv/cocotb/`` directory and place in it the C and python test files
### 6. Import the new tests to ``cocotb_tests.py``:
Add this line ``from gpio_test.gpio_test import gpio_test`` in ``caravel_user_project/verilog/dv/cocotb/cocotb_tests.py``
### 7. Run the test:
To run the test you have to be in ``caravel-sim-infrastructure/cocotb/`` directory and run the ``verify_cocotb.py`` script using the following command
```
python3 verify_cocotb.py -test gpio_test -sim RTL -tag first_test
```
You can know more about the argument options [here](https://github.com/efabless/caravel-sim-infrastructure/tree/main/cocotb#run-a-test)
### 8. Check if the test passed or failed:
When you run the above you will get this ouput:
```
test:['gpio_test'], testlist:None sim: ['RTL']
Run tag: first_test
invalid mail None
Start running test:  RTL-gpio_test 
Error: Fail to compile the C code for more info refer to /home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/firmware.log 
```
It shows that there is an error in the firmware c-code and it could'nt be compiled. You should check the `firmware.log` log file in the `caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/` directory to check any firmware errors.
In the log file you will find this error:
```
/home/nouran/caravel_user_project/verilog/dv/cocotb/gpio_test/gpio_test.c: In function 'main':
/home/nouran/caravel_user_project/verilog/dv/cocotb/gpio_test/gpio_test.c:7:24: error: 'GPIO_MODE_MGMT_STD_OUT' undeclared (first use in this function); did you mean 'GPIO_MODE_MGMT_STD_OUTPUT'?
    7 |    configure_all_gpios(GPIO_MODE_MGMT_STD_OUT);
      |                        ^~~~~~~~~~~~~~~~~~~~~~
      |                        GPIO_MODE_MGMT_STD_OUTPUT
/home/nouran/caravel_user_project/verilog/dv/cocotb/gpio_test/gpio_test.c:7:24: note: each undeclared identifier is reported only once for each function it appears in
Error: when generating hex
```
### 9. Modify the firmware:
The error was because passign the wrong gpio mode name. To fix this, you should change `configure_all_gpios(GPIO_MODE_MGMT_STD_OUT);` to `configure_all_gpios(GPIO_MODE_MGMT_STD_OUTPUT);` and rerun. 
### 10. Check if the test passed or failed:
 When you rerun you will get the following output:
 ```                                                     
Fail: Test RTL-gpio_test has Failed for more info refer to /home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/gpio_test.log
 ```

The test has failed. You should check the `compilation.log` log file in the directory `caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/`. You will find the following error message:
```
     0.00ns INFO     cocotb                              [caravel] start powering up
   225.00ns INFO     cocotb                              [caravel] power up -> connect vdd
   225.00ns INFO     cocotb                              [caravel] power up -> connect vcc
   475.00ns INFO     cocotb                              [caravel] disable housekeeping SPI transmission
   525.00ns INFO     cocotb                              [caravel] start resetting
  1050.00ns INFO     cocotb                              [caravel] finish resetting
1578050.00ns INFO     cocotb                             All gpios '00000000000000000000000000000010001111'
1578050.00ns INFO     cocotb                             [TEST] Pass the gpio value is '0x8f'
1578050.00ns INFO     cocotb                             Test passed with (0)criticals (0)errors (0)warnings 
1578050.00ns INFO     cocotb                             Cycles consumed = 63122 recommened timeout = 63754 cycles
1578050.00ns INFO     cocotb.regression                  report_test.<locals>.wrapper_func [32mpassed[49m[39m
1578050.00ns INFO     cocotb.regression                  **************************************************************************************************************************************
                                                         ** TEST                                                                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                         **************************************************************************************************************************************
                                                         ** interfaces.common_functions.test_functions.report_test.<locals>.wrapper_func  [32m PASS [49m[39m    1578050.00          40.21      39247.62  **
                                                         **************************************************************************************************************************************
                                                         ** TESTS=1 PASS=1 FAIL=0 SKIP=0                                                            1578050.00          40.22      39233.14  **
                                                         **************************************************************************************************************************************
```
This means the result weren't as expected and test failed message was raised because of the cocotb.log.error() function. 
### 11. Modify the python test bench:
The error is because the expected value (0xF8) is not equal to the gpios value (0x8F). To fix this change the expected value to 0x8F `expected_gpio_value = 0x8F` and rerun
### 12. Check if the test passed or failed:
When you rerun you will get this output:
```
     0.00ns INFO     cocotb                              [caravel] start powering up
   225.00ns INFO     cocotb                              [caravel] power up -> connect vdd
   225.00ns INFO     cocotb                              [caravel] power up -> connect vcc
   475.00ns INFO     cocotb                              [caravel] disable housekeeping SPI transmission
   525.00ns INFO     cocotb                              [caravel] start resetting
  1050.00ns INFO     cocotb                              [caravel] finish resetting
1578050.00ns INFO     cocotb                             All gpios '00000000000000000000000000000010001111'
1578050.00ns ERROR    cocotb                             [TEST] Fail the gpio value is :'0x8f' expected 0xf8
1578050.00ns INFO     cocotb.regression                  report_test.<locals>.wrapper_func [31mfailed[49m[39m
                                                         Traceback (most recent call last):
                                                           File "/home/nouran/caravel-sim-infrastructure/cocotb/interfaces/common_functions/test_functions.py", line 120, in wrapper_func
                                                             raise cocotb.result.TestComplete(f"Test failed {msg}")
                                                         cocotb.result.TestComplete: Test failed with (0)criticals (1)errors (0)warnings 
1578050.00ns INFO     cocotb.regression                  **************************************************************************************************************************************
                                                         ** TEST                                                                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                         **************************************************************************************************************************************
                                                         ** interfaces.common_functions.test_functions.report_test.<locals>.wrapper_func  [31m FAIL [49m[39m    1578050.00          40.47      38988.73  **
                                                         **************************************************************************************************************************************
                                                         ** TESTS=1 PASS=0 FAIL=1 SKIP=0                                                            1578050.00          40.49      38974.22  **
                                                         **************************************************************************************************************************************
                                                         
```

This means the test has passed you can check the `compilation.log` file in the directory `caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/` which contains all the logs (for the C firmware and python testbench) and you can see the following messages:
```
docker command for running iverilog and cocotb:
% docker run --init -u $(id -u nouran):$(id -g nouran) -it --sig-proxy=true -e COCOTB_RESULTS_FILE=/home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/seed.xml -e CARAVEL_PATH=/home/nouran/caravel//verilog -e CARAVEL_VERILOG_PATH=/home/nouran/caravel//verilog -e VERILOG_PATH=/home/nouran/caravel_mgmt_soc_litex//verilog -e PDK_ROOT=/home/nouran/OpenLane/pdks/ -e PDK=sky130A -e USER_PROJECT_VERILOG=/home/nouran/caravel_user_project/verilog -v /home/nouran/caravel-sim-infrastructure/cocotb:/home/nouran/caravel-sim-infrastructure/cocotb -v /home/nouran/caravel/:/home/nouran/caravel/ -v /home/nouran/caravel_mgmt_soc_litex/:/home/nouran/caravel_mgmt_soc_litex/ -v /home/nouran/OpenLane/pdks/:/home/nouran/OpenLane/pdks/ -v /home/nouran/caravel_user_project:/home/nouran/caravel_user_project efabless/dv:cocotb sh -ec 'cd /home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test && iverilog -Ttyp  -DUSE_POWER_PINS -DUNIT_DELAY=#1 -DCOCOTB_SIM -DFUNCTIONAL -DWAVE_GEN -DIVERILOG -Dsky130 -DCPU_TYPE_VexRISC -DCOCOTB_PATH=\"/home/nouran/caravel-sim-infrastructure/cocotb\" -DTAG=\"first_test\" -DCARAVEL_ROOT=\"/home/nouran/caravel/\" -DMCW_ROOT=\"/home/nouran/caravel_mgmt_soc_litex/\" -DUSER_PROJECT_ROOT=\"/home/nouran/caravel_user_project\" -DSIM_PATH=\"/home/nouran/caravel-sim-infrastructure/cocotb/sim/\" -DSIM=\"RTL\" -DTESTNAME=\"gpio_test\" -DFTESTNAME=\"RTL-gpio_test\" -DSIM_DIR=\"/home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test\" -DCORNER_nom  -o /home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/sim.vvp /home/nouran/caravel-sim-infrastructure/cocotb/RTL/caravel_top.sv -s caravel_top  && TESTCASE=gpio_test MODULE=module_trail  vvp -M $(cocotb-config --prefix)/cocotb/libs -m libcocotbvpi_icarus /home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/sim.vvp +USE_POWER_PINS +UNIT_DELAY=#1 +COCOTB_SIM +FUNCTIONAL +WAVE_GEN +IVERILOG +sky130 +CPU_TYPE_VexRISC +COCOTB_PATH=\"/home/nouran/caravel-sim-infrastructure/cocotb\" +TAG=\"first_test\" +CARAVEL_ROOT=\"/home/nouran/caravel/\" +MCW_ROOT=\"/home/nouran/caravel_mgmt_soc_litex/\" +USER_PROJECT_ROOT=\"/home/nouran/caravel_user_project\" +SIM_PATH=\"/home/nouran/caravel-sim-infrastructure/cocotb/sim/\" +SIM=\"RTL\" +TESTNAME=\"gpio_test\" +FTESTNAME=\"RTL-gpio_test\" +SIM_DIR=\"/home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test\" +CORNER_nom +__USER_DEFINES_H +GPIO_MODE_INVALID=0 +GPIO_MODE_MGMT_STD_INPUT_NOPULL=1027 +GPIO_MODE_MGMT_STD_INPUT_PULLDOWN=3073 +GPIO_MODE_MGMT_STD_INPUT_PULLUP=2049 +GPIO_MODE_MGMT_STD_OUTPUT=6153 +GPIO_MODE_MGMT_STD_BIDIRECTIONAL=6145 +GPIO_MODE_MGMT_STD_ANALOG=11 +GPIO_MODE_USER_STD_INPUT_NOPULL=1026 +GPIO_MODE_USER_STD_INPUT_PULLDOWN=3072 +GPIO_MODE_USER_STD_INPUT_PULLUP=2048 +GPIO_MODE_USER_STD_OUTPUT=6152 +GPIO_MODE_USER_STD_BIDIRECTIONAL=6144 +GPIO_MODE_USER_STD_OUT_MONITORED=6146 +GPIO_MODE_USER_STD_ANALOG=10 +USER_CONFIG_GPIO_5_INIT=6153 +USER_CONFIG_GPIO_6_INIT=6153 +USER_CONFIG_GPIO_7_INIT=6153 +USER_CONFIG_GPIO_8_INIT=6153 +USER_CONFIG_GPIO_9_INIT=6153 +USER_CONFIG_GPIO_10_INIT=6153 +USER_CONFIG_GPIO_11_INIT=6153 +USER_CONFIG_GPIO_12_INIT=6153 +USER_CONFIG_GPIO_13_INIT=6153 +USER_CONFIG_GPIO_14_INIT=6153 +USER_CONFIG_GPIO_15_INIT=6153 +USER_CONFIG_GPIO_16_INIT=6153 +USER_CONFIG_GPIO_17_INIT=6153 +USER_CONFIG_GPIO_18_INIT=6153 +USER_CONFIG_GPIO_19_INIT=6153 +USER_CONFIG_GPIO_20_INIT=6153 +USER_CONFIG_GPIO_21_INIT=6153 +USER_CONFIG_GPIO_22_INIT=6153 +USER_CONFIG_GPIO_23_INIT=6153 +USER_CONFIG_GPIO_24_INIT=6153 +USER_CONFIG_GPIO_25_INIT=6153 +USER_CONFIG_GPIO_26_INIT=6153 +USER_CONFIG_GPIO_27_INIT=6153 +USER_CONFIG_GPIO_28_INIT=6153 +USER_CONFIG_GPIO_29_INIT=6153 +USER_CONFIG_GPIO_30_INIT=6153 +USER_CONFIG_GPIO_31_INIT=6153 +USER_CONFIG_GPIO_32_INIT=6153 +USER_CONFIG_GPIO_33_INIT=6153 +USER_CONFIG_GPIO_34_INIT=6153 +USER_CONFIG_GPIO_35_INIT=6153 +USER_CONFIG_GPIO_36_INIT=6153 +USER_CONFIG_GPIO_37_INIT=6153 +__GLOBAL_DEFINE_H +MPRJ_IO_PADS_1=19 +MPRJ_IO_PADS_2=19 +MPRJ_IO_PADS=38 +MPRJ_PWR_PADS_1=2 +MPRJ_PWR_PADS_2=2 +MPRJ_PWR_PADS=4 +ANALOG_PADS_1=5 +ANALOG_PADS_2=6 +ANALOG_PADS=11 +USE_CUSTOM_DFFRAM +MEM_WORDS=256 +DFFRAM_WSIZE=4 +DFFRAM_USE_LATCH=0 +RAM_BLOCKS=1 +CLK_DIV=2 +MGMT_INIT=0 +OENB_INIT=0 +DM_INIT=1 +LA_SIZE=128 +USER_SPACE_ADDR=805306368 +USER_SPACE_SIZE=1048572 +IO_CTRL_BITS=13 +POWER_DOMAINS=3'

/home/nouran/caravel//verilog/rtl/caravel.v:236: warning: input port clock is coerced to inout.
     -.--ns INFO     gpi                                ..mbed/gpi_embed.cpp:76   in set_program_name_in_venv        Did not detect Python virtual environment. Using system-wide Python interpreter
     -.--ns INFO     gpi                                ../gpi/GpiCommon.cpp:101  in gpi_print_registered_impl       VPI registered
     0.00ns INFO     cocotb                             Running on Icarus Verilog version 10.3 (stable)
     0.00ns INFO     cocotb                             Running tests with cocotb v1.7.1 from /usr/local/lib/python3.8/dist-packages/cocotb
     0.00ns INFO     cocotb                             Seeding Python random module with 1684245124
     0.00ns INFO     cocotb.regression                  pytest not found, install it to enable better AssertionError messages
     0.00ns INFO     cocotb.regression                  Found test interfaces.common_functions.test_functions.report_test.<locals>.wrapper_func
     0.00ns INFO     cocotb.regression                  running report_test.<locals>.wrapper_func (1/1)
/home/nouran/caravel-sim-infrastructure/cocotb/interfaces/common_functions/Timeout.py:19: DeprecationWarning: This method is now private.
  cocotb.scheduler.add(self._timeout_check())
/home/nouran/caravel-sim-infrastructure/cocotb/interfaces/common_functions/test_functions.py:59: DeprecationWarning: This method is now private.
  cocotb.scheduler.add(max_num_error(num_error, caravelEnv.clk))
     0.00ns INFO     cocotb                              [caravel] start powering up
Reading /home/nouran/caravel-sim-infrastructure/cocotb/sim//hex_files/gpio_test.hex
/home/nouran/caravel-sim-infrastructure/cocotb/sim//hex_files/gpio_test.hex loaded into memory
Memory 5 bytes = 0x6f 0x00 0x00 0x0b 0x13
VCD info: dumpfile /home/nouran/caravel-sim-infrastructure/cocotb/sim/first_test/RTL-gpio_test/RTL-gpio_test.vcd opened for output.
   225.00ns INFO     cocotb                              [caravel] power up -> connect vdd
   225.00ns INFO     cocotb                              [caravel] power up -> connect vcc
 ===WARNING=== sky130_fd_io__top_xres4v2 :  Width of Input pulse for PAD input (= 225.00 ns)  is found to be in 	he range:  50 ns - 600 ns. In this range, the delay and pulse suppression of the input pulse are PVT dependent. : caravel_top.uut.padframe.resetb_pad       225
   475.00ns INFO     cocotb                              [caravel] disable housekeeping SPI transmission
   525.00ns INFO     cocotb                              [caravel] start resetting
 ===WARNING=== sky130_fd_io__top_xres4v2 :  Width of Input pulse for PAD input (= 300.00 ns)  is found to be in 	he range:  50 ns - 600 ns. In this range, the delay and pulse suppression of the input pulse are PVT dependent. : caravel_top.uut.padframe.resetb_pad       525
 ===WARNING=== sky130_fd_io__top_xres4v2 :  Width of Input pulse for PAD input (= 500.00 ns)  is found to be in 	he range:  50 ns - 600 ns. In this range, the delay and pulse suppression of the input pulse are PVT dependent. : caravel_top.uut.padframe.resetb_pad      1025
  1050.00ns INFO     cocotb                              [caravel] finish resetting
1578050.00ns INFO     cocotb                             All gpios '00000000000000000000000000000010001111'
1578050.00ns INFO     cocotb                             [TEST] Pass the gpio value is '0x8f'
1578050.00ns INFO     cocotb                             Test passed with (0)criticals (0)errors (0)warnings 
1578050.00ns INFO     cocotb                             Cycles consumed = 63122 recommened timeout = 63754 cycles
1578050.00ns INFO     cocotb.regression                  report_test.<locals>.wrapper_func passed
1578050.00ns INFO     cocotb.regression                  **************************************************************************************************************************************
                                                         ** TEST                                                                          STATUS  SIM TIME (ns)  REAL TIME (s)  RATIO (ns/s) **
                                                         **************************************************************************************************************************************
                                                         ** interfaces.common_functions.test_functions.report_test.<locals>.wrapper_func   PASS     1578050.00          40.21      39247.62  **
                                                         **************************************************************************************************************************************
                                                         ** TESTS=1 PASS=1 FAIL=0 SKIP=0                                                            1578050.00          40.22      39233.14  **
                                                         **************************************************************************************************************************************
```
which shows that the test has passed successfully. 
