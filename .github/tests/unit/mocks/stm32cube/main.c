#include "CppUTestExt/MockSupport_c.h"
#include "main.h"

// Peripheral handle instances
ADC_HandleTypeDef hadc1 = {0};
UART_HandleTypeDef huart2 = {0};
TIM_HandleTypeDef htim2 = {0};
TIM_HandleTypeDef htim3 = {0};

// Test spy for tick simulation
static uint32_t currentTicks = 0;

HAL_StatusTypeDef HAL_Init(void)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_Init")
        ->returnIntValueOrDefault(0);
}

void SystemClock_Config(void)
{
    mock_c()
        ->actualCall("SystemClock_Config");
}

void MX_GPIO_Init(void)
{
    mock_c()
        ->actualCall("MX_GPIO_Init");
}

void MX_USART2_UART_Init(void)
{
    mock_c()
        ->actualCall("MX_USART2_UART_Init");
}

uint32_t HAL_GetTick(void)
{
    mock_c()->actualCall("HAL_GetTick");
    return currentTicks;
}

void HAL_GPIO_TogglePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin)
{
    mock_c()
        ->actualCall("HAL_GPIO_TogglePin")
        ->withPointerParameters("GPIOx", GPIOx)
        ->withIntParameters("GPIO_Pin", GPIO_Pin);
}

GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin)
{
    return (GPIO_PinState)mock_c()
        ->actualCall("HAL_GPIO_ReadPin")
        ->withPointerParameters("GPIOx", GPIOx)
        ->withIntParameters("GPIO_Pin", GPIO_Pin)
        ->returnIntValueOrDefault(GPIO_PIN_RESET);
}

void HAL_GPIO_WritePin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin, GPIO_PinState PinState)
{
    mock_c()
        ->actualCall("HAL_GPIO_WritePin")
        ->withPointerParameters("GPIOx", GPIOx)
        ->withIntParameters("GPIO_Pin", GPIO_Pin)
        ->withIntParameters("PinState", PinState);
}

void HAL_Delay(uint32_t Delay)
{
    mock_c()
        ->actualCall("HAL_Delay")
        ->withUnsignedIntParameters("Delay", Delay);
}

HAL_StatusTypeDef HAL_TIM_Base_Start_IT(TIM_HandleTypeDef *htim)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_TIM_Base_Start_IT")
        ->withPointerParameters("htim", htim)
        ->returnIntValueOrDefault(0);
}

HAL_StatusTypeDef HAL_TIM_OC_Start(TIM_HandleTypeDef *htim, uint32_t Channel)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_TIM_OC_Start")
        ->withPointerParameters("htim", htim)
        ->withUnsignedIntParameters("Channel", Channel)
        ->returnIntValueOrDefault(0);
}

HAL_StatusTypeDef HAL_TIM_PWM_Start(TIM_HandleTypeDef *htim, uint32_t Channel)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_TIM_PWM_Start")
        ->withPointerParameters("htim", htim)
        ->withUnsignedIntParameters("Channel", Channel)
        ->returnIntValueOrDefault(0);
}

HAL_StatusTypeDef HAL_TIM_PWM_Stop(TIM_HandleTypeDef *htim, uint32_t Channel)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_TIM_PWM_Stop")
        ->withPointerParameters("htim", htim)
        ->withUnsignedIntParameters("Channel", Channel)
        ->returnIntValueOrDefault(0);
}

HAL_StatusTypeDef HAL_ADC_Start_DMA(ADC_HandleTypeDef *hadc, uint32_t *pData, uint32_t Length)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_ADC_Start_DMA")
        ->withPointerParameters("hadc", hadc)
        ->withPointerParameters("pData", pData)
        ->withUnsignedIntParameters("Length", Length)
        ->returnIntValueOrDefault(0);
}

HAL_StatusTypeDef HAL_TIM_Base_Start(TIM_HandleTypeDef *htim)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_TIM_Base_Start")
        ->withPointerParameters("htim", htim)
        ->returnIntValueOrDefault(0);
}

HAL_StatusTypeDef HAL_UART_Transmit(UART_HandleTypeDef *huart, uint8_t *pData, uint16_t Size, uint32_t Timeout)
{
    return (HAL_StatusTypeDef)mock_c()
        ->actualCall("HAL_UART_Transmit")
        ->withPointerParameters("huart", huart)
        ->withPointerParameters("pData", pData)
        ->withUnsignedIntParameters("Size", Size)
        ->withUnsignedIntParameters("Timeout", Timeout)
        ->returnIntValueOrDefault(0);
}

void SPY_setCurrentTicks(uint32_t ticks)
{
    currentTicks = ticks;
}