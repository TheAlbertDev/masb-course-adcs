#ifndef Arduino_H__
#define Arduino_H__

#include <stdint.h>
#include <math.h>

#define OUTPUT 0x1
#define INPUT 0x0
#define LOW 0x0
#define HIGH 0x1
#define CHANGE 0x2
#define FALLING 0x3
#define RISING 0x4

// Analog pin definitions
#define A0 14
#define A1 15

// Timer definitions
#define TIM2 2
#define TIM3 3
#define TIMER_OUTPUT_COMPARE 0x10
#define TIMER_OUTPUT_COMPARE_TOGGLE 0x11
#define MICROSEC_FORMAT 0x20

typedef void (*callback_function_t)(void);

// Callback spy functions for testing
callback_function_t SPY_ARDUINO_GetLastAttachedCallback(void);
void SPY_ARDUINO_ClearLastAttachedCallback(void);

// HardwareTimer spy functions for testing
class HardwareTimer;
HardwareTimer *SPY_HARDWARE_TIMER_GetLastCreatedInstance(void);
void SPY_HARDWARE_TIMER_ClearLastCreatedInstance(void);

// Basic Arduino functions
void delay(uint32_t ms);
unsigned long millis(void);
void digitalWrite(uint32_t dwPin, uint32_t dwVal);
void pinMode(uint32_t dwPin, uint32_t dwMode);
int digitalRead(uint32_t ulPin);
uint32_t analogRead(uint32_t ulPin);
void attachInterrupt(uint32_t pin, callback_function_t callback, uint32_t mode);
void detachInterrupt(uint32_t pin);
uint32_t digitalPinToInterrupt(uint32_t pin);

// HardwareTimer class mock
class HardwareTimer
{
public:
    HardwareTimer(uint32_t timer);
    void setMode(uint32_t channel, uint32_t mode, uint32_t pin = 0);
    void setOverflow(uint32_t period, uint32_t format);
    void attachInterrupt(callback_function_t callback);
    void resume();
    void pause();
    void setCount(uint32_t count);
    void setPWM(uint32_t channel, uint32_t pin, uint32_t frequency, double duty);

private:
    uint32_t timer_id;
};

// HardwareSerial class mock
class HardwareSerial
{
public:
    void begin(uint32_t baud);
    void print(const char *str);
    void print(uint32_t val);
    void println(const char *str);
    void println(uint32_t val);
};

extern HardwareSerial Serial;

#endif /* Arduino_H__ */