#ifndef Main_H__
#define Main_H__

#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "CppUTestExt/MockSupport_c.h"

#ifdef __cplusplus
extern "C" {
#endif

#define LED_GPIO_Port ((GPIO_TypeDef *)0x40020000)
#define LED_Pin 0x0020
#define PUSH_BUTTON_Pin 0x2000
#define PUSH_BUTTON_GPIO_Port ((GPIO_TypeDef *)0x40020000)

// Timer channel definitions
#define TIM_CHANNEL_1 0x00000000U

// ADC handle type
typedef struct
{
    uint32_t Instance;
    uint32_t Init;
    uint32_t State;
} ADC_HandleTypeDef;

// UART handle type
typedef struct
{
    uint32_t Instance;
    uint32_t Init;
    uint32_t State;
} UART_HandleTypeDef;

// Timer types
typedef struct
{
    uint32_t Instance;
    uint32_t Init;
    uint32_t lock;
    uint32_t State;
    uint32_t Channel;
    uint32_t DMABurstState;
} TIM_HandleTypeDef;

typedef uint32_t GPIO_TypeDef;
typedef uint32_t HAL_StatusTypeDef;
typedef enum
{
    GPIO_PIN_RESET = 0,
    GPIO_PIN_SET
} GPIO_PinState;

// Basic HAL functions
HAL_StatusTypeDef HAL_Init(void);
void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_USART2_UART_Init(void);

uint32_t HAL_GetTick(void);
void HAL_GPIO_TogglePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
void HAL_GPIO_WritePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState);
void HAL_Delay(uint32_t Delay);

// ADC functions
HAL_StatusTypeDef HAL_ADC_Start_DMA(ADC_HandleTypeDef *hadc, uint32_t *pData, uint32_t Length);

// Timer functions
HAL_StatusTypeDef HAL_TIM_Base_Start(TIM_HandleTypeDef *htim);
HAL_StatusTypeDef HAL_TIM_Base_Start_IT(TIM_HandleTypeDef *htim);
HAL_StatusTypeDef HAL_TIM_OC_Start(TIM_HandleTypeDef *htim, uint32_t Channel);
HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *htim, uint32_t Channel);
HAL_StatusTypeDef HAL_TIM_PWM_Stop(TIM_HandleTypeDef *htim, uint32_t Channel);

// Timer comparison macros using C interface
#define __HAL_TIM_SET_COMPARE(htim, channel, compare) \
    mock_c()->actualCall("__HAL_TIM_SET_COMPARE")->withPointerParameters("htim", htim)->withUnsignedIntParameters("channel", channel)->withUnsignedIntParameters("compare", compare)

#define __HAL_TIM_SET_COUNTER(htim, counter) \
    mock_c()->actualCall("__HAL_TIM_SET_COUNTER")->withPointerParameters("htim", htim)->withUnsignedIntParameters("counter", counter)

// Timer callbacks (implemented in user code)
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim);

// UART functions
HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *huart, uint8_t *pData, uint16_t Size, uint32_t Timeout);

// Test spy functions
void SPY_setCurrentTicks(uint32_t ticks);

// External declarations for peripheral handles
extern ADC_HandleTypeDef hadc1;
extern UART_HandleTypeDef huart2;
extern TIM_HandleTypeDef htim2;
extern TIM_HandleTypeDef htim3;

// User application functions
void setup(void);
void loop(void);

#ifdef __cplusplus
}
#endif

#endif /* Main_H__ */