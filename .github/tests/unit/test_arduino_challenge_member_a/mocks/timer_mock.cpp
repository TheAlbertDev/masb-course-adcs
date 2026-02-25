#include "CppUTestExt/MockSupport.h"
#include "timer.h"

void TIMER_Init(void)
{
    mock().actualCall("TIMER_Init");
}
