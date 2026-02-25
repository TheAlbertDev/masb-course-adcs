#include "CppUTest/TestHarness.h"
#include "CppUTestExt/MockSupport.h"
#include "Arduino.h"
#include "adc.h"

// Project source file functions
extern void GPIO_Init(void);
extern void toggleStateADC(void);
extern void TIMER_Init(void);
extern void startAdcConversion(void);

// ============================================================
// Tests for gpio.cpp
// ============================================================

TEST_GROUP(GpioMemberB) // clang-format off
{
    void setup()
    {
        SPY_ARDUINO_ClearLastAttachedCallback();
        mock().ignoreOtherCalls();
    }

    void teardown()
    {
        HardwareTimer *tim = SPY_HARDWARE_TIMER_GetLastCreatedInstance();
        if (tim != nullptr)
        {
            delete tim;
            SPY_HARDWARE_TIMER_ClearLastCreatedInstance();
        }
        mock().clear();
        SPY_ARDUINO_ClearLastAttachedCallback();
    }
}; // clang-format on

TEST(GpioMemberB, GPIO_Init_Configures_PUSH_Pin_As_Input)
{
    // GPIO_Init() must configure pin 23 (PUSH) as INPUT
    mock().expectOneCall("pinMode")
        .withParameter("dwPin", (uint32_t)23)
        .withParameter("dwMode", (uint32_t)INPUT);

    GPIO_Init();

    mock().checkExpectations();
}

TEST(GpioMemberB, GPIO_Init_Attaches_Interrupt_Handler)
{
    // GPIO_Init() must register an ISR for the button pin
    GPIO_Init();

    CHECK(SPY_ARDUINO_GetLastAttachedCallback() != nullptr);
}

TEST(GpioMemberB, ToggleStateADC_Enables_ADC_When_Disabled)
{
    // When ADC is off, pressing the button must enable it
    mock().expectOneCall("getOnADC").andReturnValue(false);
    mock().expectOneCall("setOnADC").withParameter("state", true);

    toggleStateADC();

    mock().checkExpectations();
}

TEST(GpioMemberB, ToggleStateADC_Disables_ADC_When_Enabled)
{
    // When ADC is on, pressing the button must disable it
    mock().expectOneCall("getOnADC").andReturnValue(true);
    mock().expectOneCall("setOnADC").withParameter("state", false);

    toggleStateADC();

    mock().checkExpectations();
}

// ============================================================
// Tests for timer.cpp
// ============================================================

TEST_GROUP(TimerMemberB) // clang-format off
{
    void setup()
    {
        mock().ignoreOtherCalls();
    }

    void teardown()
    {
        HardwareTimer *tim = SPY_HARDWARE_TIMER_GetLastCreatedInstance();
        if (tim != nullptr)
        {
            delete tim;
            SPY_HARDWARE_TIMER_ClearLastCreatedInstance();
        }
        mock().clear();
    }
}; // clang-format on

TEST(TimerMemberB, TIMER_Init_Creates_TIM3_Hardware_Timer)
{
    // TIMER_Init() must create a HardwareTimer using TIM3
    mock().expectOneCall("HardwareTimer::constructor")
        .withParameter("timer", (uint32_t)TIM3);

    TIMER_Init();

    mock().checkExpectations();
}

TEST(TimerMemberB, TIMER_Init_Configures_100ms_Period)
{
    // TIMER_Init() must set a 100 ms overflow period (100000 µs)
    mock().expectOneCall("HardwareTimer::setOverflow")
        .withParameter("period", (uint32_t)100000)
        .withParameter("format", (uint32_t)MICROSEC_FORMAT);

    TIMER_Init();

    mock().checkExpectations();
}

TEST(TimerMemberB, TIMER_Init_Attaches_ISR)
{
    // TIMER_Init() must attach an ISR callback to the timer
    mock().expectOneCall("HardwareTimer::attachInterrupt").ignoreOtherParameters();

    TIMER_Init();

    mock().checkExpectations();
}

TEST(TimerMemberB, TIMER_Init_Starts_Timer)
{
    // TIMER_Init() must start the timer by calling resume()
    mock().expectOneCall("HardwareTimer::resume");

    TIMER_Init();

    mock().checkExpectations();
}

TEST(TimerMemberB, StartAdcConversion_Calls_ConversionADC)
{
    // The timer ISR must trigger an ADC conversion attempt
    mock().expectOneCall("conversionADC");

    startAdcConversion();

    mock().checkExpectations();
}
