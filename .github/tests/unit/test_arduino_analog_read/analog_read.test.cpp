#include "CppUTest/TestHarness.h"
#include "CppUTestExt/MockSupport.h"
#include "Arduino.h"

// Project source file functions
extern void setup(void);
extern void loop(void);

TEST_GROUP(AnalogRead) // clang-format off
{
    void setup()
    {
    
    }

    void teardown()
    {
        mock().clear();
    }
}; // clang-format on

TEST(AnalogRead, Setup_Is_Empty)
{
    // setup() must not call any functions — all work is done in loop()

    ::setup();

    mock().checkExpectations();
}

TEST(AnalogRead, Loop_Calls_AnalogRead_On_A0)
{
    // loop() must call analogRead once with pin A0
    mock().expectOneCall("analogRead").withParameter("ulPin", A0).andReturnValue(512);

    ::loop();

    mock().checkExpectations();
}
