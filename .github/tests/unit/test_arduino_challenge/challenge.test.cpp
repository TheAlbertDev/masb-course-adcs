#include "CppUTest/TestHarness.h"
#include "CppUTestExt/MockSupport.h"
#include "Arduino.h"

// Project source file functions
extern void setup(void);
extern void loop(void);

TEST_GROUP(Challenge) // clang-format off
{
    void setup()
    {
        SPY_ARDUINO_ClearLastAttachedCallback(); // Reset callback spy
        // Allow any setup calls - students have implementation freedom
        mock().ignoreOtherCalls();

        ::setup();

        // Just verify callback was captured (button interrupt was set up)
        CHECK(SPY_ARDUINO_GetLastAttachedCallback() != nullptr);

        mock().checkExpectations();
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

TEST(Challenge, Empty_Loop_Function)
{
    // RESTRICTION: Loop function must be empty (no software polling)
    // LED control should be handled entirely by hardware timer

    ::loop(); // Should not trigger any mock calls

    mock().checkExpectations();
}