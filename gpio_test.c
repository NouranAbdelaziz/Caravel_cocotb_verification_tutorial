#include <firmware_apis.h> // include required APIs
void main(){
 // Enable managment gpio as output to use as indicator for finishing configuration 
  ManagmentGpio_outputEnable();
  ManagmentGpio_write(0);
  enableHkSpi(0); // disable housekeeping spi
  GPIOs_configureAll(GPIO_MODE_MGMT_STD_OUTPUT);  //GPIOs_configureAll(GPIO_MODE_MGMT_STD_OUT);
  GPIOs_loadConfigs();
  GPIOs_writeLow(0x8F);
  ManagmentGpio_write(1); // configuration finished 
  return;
}
