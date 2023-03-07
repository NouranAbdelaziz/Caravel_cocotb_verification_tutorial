# Caravel cocotb verification tutorial

This tutorial will show you how to use cocotb Caravel APIs in order to create a testbench which sets Caravel gpios to have a certain value.

## The steps: 

### 1. Install prerequisites:
Make sure you followed the [quickstart guide]() to install the prerequisites and cloned the [cocotb verification repo]() 
### 2. Update design_info.yaml file:
Make sure you updated the paths inside the ``design_info.yaml`` to match your paths as shown [here](). You can find the file in the ```caravel-dynamic-sims/cocotb/``` directory
### 3. Create the firmware program:
The firmware is written in C code and it is the program that will be running on the Caravel management SoC. You can use it to make any configurations you want. You can find a description for all the firmware C APIs [here]()
For example, you can use it to configure the GPIO pins to have a certain value as shown in the code below:
```
#include <common.h> 
void main(){
  mgmt_gpio_o_enable();
  mgmt_gpio_wr(0);
  enable_hk_spi(0); 
  configure_all_gpios(GPIO_MODE_MGMT_STD_OUTPUT);
  gpio_config_load();
  set_gpio_l(0x8F);
  mgmt_gpio_wr(1);
  return;
}
```
* ``#include <common.h>``  is used to include the firmware APIs. This must be included in any firmware that will use the APIs provided. 
* ``mgmt_gpio_o_enable();`` is a function used to set the management gpio to output (this is a single gpio pin inside used by the management soc). You can read more about this function [here](). 
* ``mgmt_gpio_wr(0);`` is a function to set the management gpio pin to a certain value. Here I am setting it to 0 and later will set it to 1 after the configurations are finished. This is to make sure in the python testbench that the configurations are done and you can begin to check the gpios value. You can read more about this function [here](). 
* ``configure_all_gpios(GPIO_MODE_MGMT_STD_OUTPUT);`` is a function used to configure all caravel’s 38 gpio pins with a certain mode. Here I chose the ``GPIO_MODE_MGMT_STD_OUTPUT`` mode because I will use the gpios as output and the management SoC will be the one using the gpios not the user project. You can read more about this function [here](). 
* ``gpio_config_load();`` is a function to load the gpios configuration. It must be called whenever we change gpio configuration. 
* ``set_gpio_l(0x8F);`` is a function used to set the value of the lower 32 gpios with a certain value. In this example the first 4 gpios and the 8th gpio will be set to 1 and the rest will be set to 0. you can read more about this function [here](). 
* ``mgmt_gpio_wr(1);`` is a function to set the management gpio to 1 to indicate configurations are done as explained above.

### 4. Create the python testbench:
The python testbench is used to monitor the signals of the Caravel chip just like the testbenches used in hardware simulators. 
Continuing on the example above,  if we want to check whether the gpios are set to the correct value, we can do that using the following code:

```
from cocotb_includes import *
import cocotb

@cocotb.test()
@repot_test
async def gpio_test(dut):
  caravelEnv = await test_configure(dut)
  await caravelEnv.release_csb()
  await caravelEnv.wait_mgmt_gpio(1)
  cocotb.log.info("Hello !")
  gpio_value = int (caravelEnv.monitor_gpio(7).binstr, 2)
  all_gpios = caravelEnv.monitor_gpio(37, 0).binstr
  cocotb.log.info (f"All gpios '{all_gpios}'")
  if (gpio_value == 1):
     cocotb.log.info (f"[TEST] Pass the gpio value is '{gpio_value}'")
  else:
     cocotb.log.error (f"[TEST] Fail the gpio value is :'{gpio_value}' expected 1")
```
* 
### 5. Run the test:
### 6. Check if the test passed or failed:
failed because an error in the c code
### 7. Modify the firmware:
### 8. Check if the test passed or failed:
failed because the value of the gpio is different 
### 9. Modify the python test bench:
### 8. Check if the test passed or failed:
passed !!

