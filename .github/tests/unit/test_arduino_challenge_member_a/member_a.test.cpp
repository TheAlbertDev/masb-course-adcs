#include "CppUTest/TestHarness.h"
#include "CppUTestExt/MockSupport.h"
#include "Arduino.h"
#include "adc.h"

// Project source file functions
extern void setup(void);
extern void loop(void);

// ============================================================
// Tests for main.cpp
// ============================================================

TEST_GROUP(MainMemberA) // clang-format off
{
    void setup()
    {
    }

    void teardown()
    {
        mock().clear();
    }
}; // clang-format on

TEST(MainMemberA, Setup_Calls_TIMER_Init)
{
    mock().expectOneCall("TIMER_Init");
    mock().ignoreOtherCalls();

    ::setup();

    mock().checkExpectations();
}

TEST(MainMemberA, Setup_Calls_GPIO_Init)
{
    mock().expectOneCall("GPIO_Init");
    mock().ignoreOtherCalls();

    ::setup();

    mock().checkExpectations();
}

TEST(MainMemberA, Setup_Initializes_Serial_Communication)
{
    // setup() must initialize serial at 9600 baud
    mock().expectOneCall("Serial::begin").withParameter("baud", (uint32_t)9600);
    mock().ignoreOtherCalls();

    ::setup();

    mock().checkExpectations();
}

TEST(MainMemberA, Loop_Does_Not_Call_Any_Functions)
{
    // loop() must be empty — all logic is handled via interrupts

    ::loop();

    mock().checkExpectations();
}

// ============================================================
// Tests for adc.cpp
// ============================================================

TEST_GROUP(AdcMemberA) // clang-format off
{
    void setup()
    {
        setOnADC(false); // ensure clean initial state
    }

    void teardown()
    {
        setOnADC(false); // reset static state
        mock().clear();
    }
}; // clang-format on

TEST(AdcMemberA, SetOnADC_And_GetOnADC_Work_Correctly)
{
    // Verify the getter/setter pair behaves correctly
    setOnADC(false);
    CHECK_FALSE(getOnADC());

    setOnADC(true);
    CHECK_TRUE(getOnADC());

    setOnADC(false);
    CHECK_FALSE(getOnADC());
}

TEST(AdcMemberA, ConversionADC_Does_Not_Read_ADC_When_Disabled)
{
    // When ADC is off, conversionADC() must not call analogRead

    setOnADC(false);
    conversionADC();

    mock().checkExpectations(); // no unexpected calls
}

TEST(AdcMemberA, ConversionADC_Reads_A0_When_Enabled)
{
    // When ADC is on, conversionADC() must call analogRead on pin A0
    setOnADC(true);

    mock().expectOneCall("analogRead")
        .withParameter("ulPin", (uint32_t)A0)
        .andReturnValue((unsigned int)512);
    mock().ignoreOtherCalls(); // ignore Serial calls

    conversionADC();

    mock().checkExpectations();
}

TEST(AdcMemberA, ConversionADC_Sends_Serial_Label_When_Enabled)
{
    // When ADC is on, conversionADC() must send the Teleplot label ">valAdc:"
    setOnADC(true);

    mock().expectOneCall("Serial::print").withParameter("str", ">valAdc:");
    mock().ignoreOtherCalls(); // ignore analogRead and Serial::println

    conversionADC();

    mock().checkExpectations();
}
