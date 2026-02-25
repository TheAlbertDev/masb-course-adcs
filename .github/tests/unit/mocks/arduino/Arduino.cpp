#include "CppUTestExt/MockSupport.h"
#include "Arduino.h"

// Private spy storage - not exposed globally
static callback_function_t s_lastAttachedCallback = nullptr;
static HardwareTimer *s_lastCreatedHardwareTimer = nullptr;

void pinMode(uint32_t ulPin, uint32_t ulMode)
{
    mock()
        .actualCall("pinMode")
        .withParameter("dwPin", ulPin)
        .withParameter("dwMode", ulMode);
    return;
}

void digitalWrite(uint32_t ulPin, uint32_t ulVal)
{
    mock()
        .actualCall("digitalWrite")
        .withParameter("dwPin", ulPin)
        .withParameter("dwVal", ulVal);
    return;
}

void delay(uint32_t ms)
{
    mock()
        .actualCall("delay")
        .withParameter("ms", ms);
    return;
}

unsigned long millis(void)
{
    return mock()
        .actualCall("millis")
        .returnUnsignedLongIntValueOrDefault(0);
}

int digitalRead(uint32_t ulPin)
{
    return mock()
        .actualCall("digitalRead")
        .withParameter("ulPin", ulPin)
        .returnIntValueOrDefault(LOW);
}

uint32_t analogRead(uint32_t ulPin)
{
    return mock()
        .actualCall("analogRead")
        .withParameter("ulPin", ulPin)
        .returnUnsignedIntValueOrDefault(0);
}

void attachInterrupt(uint32_t pin, callback_function_t callback, uint32_t mode)
{
    // Store callback for testing
    s_lastAttachedCallback = callback;

    mock()
        .actualCall("attachInterrupt")
        .withParameter("pin", pin)
        .withParameter("callback", callback)
        .withParameter("mode", mode);
    return;
}

void detachInterrupt(uint32_t pin)
{
    s_lastAttachedCallback = nullptr; // Clear callback on detach

    mock()
        .actualCall("detachInterrupt")
        .withParameter("pin", pin);
    return;
}

uint32_t digitalPinToInterrupt(uint32_t pin)
{
    return mock()
        .actualCall("digitalPinToInterrupt")
        .withParameter("pin", pin)
        .returnUnsignedIntValueOrDefault(pin);
}

// Spy functions implementation
callback_function_t SPY_ARDUINO_GetLastAttachedCallback(void)
{
    return s_lastAttachedCallback;
}

void SPY_ARDUINO_ClearLastAttachedCallback(void)
{
    s_lastAttachedCallback = nullptr;
}

// HardwareTimer class implementation
HardwareTimer::HardwareTimer(uint32_t timer) : timer_id(timer)
{
    s_lastCreatedHardwareTimer = this;

    mock()
        .actualCall("HardwareTimer::constructor")
        .onObject(this)
        .withParameter("timer", timer)
        .returnPointerValueOrDefault(this);
}

HardwareTimer *SPY_HARDWARE_TIMER_GetLastCreatedInstance(void)
{
    return s_lastCreatedHardwareTimer;
}

void SPY_HARDWARE_TIMER_ClearLastCreatedInstance(void)
{
    s_lastCreatedHardwareTimer = nullptr;
}

void HardwareTimer::setMode(uint32_t channel, uint32_t mode, uint32_t pin)
{
    mock()
        .actualCall("HardwareTimer::setMode")
        .onObject(this)
        .withParameter("channel", channel)
        .withParameter("mode", mode)
        .withParameter("pin", pin);
}

void HardwareTimer::setOverflow(uint32_t period, uint32_t format)
{
    mock()
        .actualCall("HardwareTimer::setOverflow")
        .onObject(this)
        .withParameter("period", period)
        .withParameter("format", format);
}

void HardwareTimer::attachInterrupt(callback_function_t callback)
{
    mock()
        .actualCall("HardwareTimer::attachInterrupt")
        .onObject(this)
        .withParameter("callback", callback);
}

void HardwareTimer::resume()
{
    mock()
        .actualCall("HardwareTimer::resume")
        .onObject(this);
}

void HardwareTimer::pause()
{
    mock()
        .actualCall("HardwareTimer::pause")
        .onObject(this);
}

void HardwareTimer::setCount(uint32_t count)
{
    mock()
        .actualCall("HardwareTimer::setCount")
        .onObject(this)
        .withParameter("count", count);
}

void HardwareTimer::setPWM(uint32_t channel, uint32_t pin, uint32_t frequency, double duty)
{
    mock()
        .actualCall("HardwareTimer::setPWM")
        .onObject(this)
        .withParameter("channel", channel)
        .withParameter("pin", pin)
        .withParameter("frequency", frequency)
        .withParameter("duty", duty);
}

// HardwareSerial global instance
HardwareSerial Serial;

void HardwareSerial::begin(uint32_t baud)
{
    mock()
        .actualCall("Serial::begin")
        .withParameter("baud", baud);
}

void HardwareSerial::print(const char *str)
{
    mock()
        .actualCall("Serial::print")
        .withParameter("str", str);
}

void HardwareSerial::print(uint32_t val)
{
    mock()
        .actualCall("Serial::print")
        .withParameter("val", (int)val);
}

void HardwareSerial::println(const char *str)
{
    mock()
        .actualCall("Serial::println")
        .withParameter("str", str);
}

void HardwareSerial::println(uint32_t val)
{
    mock()
        .actualCall("Serial::println")
        .withParameter("val", (int)val);
}