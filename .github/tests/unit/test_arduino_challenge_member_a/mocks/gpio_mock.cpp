#include "CppUTestExt/MockSupport.h"
#include "gpio.h"

void GPIO_Init(void)
{
    mock().actualCall("GPIO_Init");
}
