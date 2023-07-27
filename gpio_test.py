from caravel_cocotb.caravel_interfaces import test_configure
from caravel_cocotb.caravel_interfaces import report_test
from caravel_cocotb.caravel_interfaces import UART
from caravel_cocotb.caravel_interfaces import SPI
import cocotb
@cocotb.test() # decorator to mark the test function as cocotb test
@report_test # wrapper for configure test reporting files
async def gpio_test(dut):
   caravelEnv = await test_configure(dut) #configure, start up and reset Caravel
   await caravelEnv.release_csb()
   await caravelEnv.wait_mgmt_gpio(1)
   gpios_value_str = caravelEnv.monitor_gpio(37, 0).binstr
   cocotb.log.info (f"All gpios '{gpios_value_str}'")
   gpio_value_int = caravelEnv.monitor_gpio(37, 0).integer
   expected_gpio_value = 0x8F
   if (gpio_value_int == expected_gpio_value):
      cocotb.log.info (f"[TEST] Pass the gpio value is '{hex(gpio_value_int)}'")
   else:
      cocotb.log.error (f"[TEST] Fail the gpio value is :'{hex(gpio_value_int)}' expected {hex(expected_gpio_value)}")
   

