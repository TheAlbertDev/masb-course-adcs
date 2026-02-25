#include "CppUTestExt/MockSupport.h"
#include "adc.h"

void conversionADC(void)
{
    mock().actualCall("conversionADC");
}

void setOnADC(bool state)
{
    mock()
        .actualCall("setOnADC")
        .withParameter("state", state);
}

bool getOnADC(void)
{
    return mock()
        .actualCall("getOnADC")
        .returnBoolValueOrDefault(false);
}
