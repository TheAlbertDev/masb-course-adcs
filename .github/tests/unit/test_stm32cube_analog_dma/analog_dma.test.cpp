#include "CppUTest/TestHarness.h"
#include "CppUTestExt/MockSupport.h"

extern "C" {
#include "main.h"
extern void setup(void);
extern void loop(void);
extern uint16_t potADC;
}

TEST_GROUP(AnalogDma) // clang-format off
{
    void setup()
    {
    }

    void teardown()
    {
        mock().clear();
    }
}; // clang-format on

TEST(AnalogDma, Setup_Calls_HAL_ADC_Start_DMA)
{
    // setup() must use DMA to start ADC conversions, not polling
    mock().expectOneCall("HAL_ADC_Start_DMA")
          .withPointerParameter("hadc", &hadc1)
          .withPointerParameter("pData", &potADC)
          .withUnsignedIntParameter("Length", 1);
    mock().ignoreOtherCalls();

    ::setup();

    mock().checkExpectations();
}

TEST(AnalogDma, Setup_Calls_HAL_TIM_Base_Start)
{
    // setup() must start the timer that triggers ADC conversions
    mock().expectOneCall("HAL_TIM_Base_Start")
          .withPointerParameter("htim", &htim2);
    mock().ignoreOtherCalls();

    ::setup();

    mock().checkExpectations();
}
