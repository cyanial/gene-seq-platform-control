#include <stdint.h>
#include <stdbool.h>

#include "flowcelltemp.h"
#include "MAX31865.h"
#include "tim.h"


bool TempControl_Running = false;

// 10 1000 500
// ki 0.01 0.1
float kp = 700.0f;
float ki = 0.3f;
float kd = 200.0f;

// PID - calc parameters
float err = 0.0f;
float sum_err = 0.0f;
float last_temp = 0.0f;
float pid_output = 0.0f;
uint16_t pwmOutput = 0;

// Temperature Read
Max31865_t pt100;
float flowcell_temp = 0.0f;
float setup_temp = 37.0f; 

// PI (D)
static uint16_t CalcTempPID()
{
	err = setup_temp - flowcell_temp;
	
  sum_err += err;
	if (sum_err >= 1000.0f) sum_err = 1000.0f;
	if (sum_err <= -1000.0f) sum_err = -1000.0f;
	
	pid_output = kp*err + ki*sum_err+kd*(flowcell_temp - last_temp); 
	
	
	if (pid_output > 1980.0f) return pwmOutput = 1999;
	if (pid_output < 30.0f) return pwmOutput = 0;
	
	return pwmOutput = (uint16_t) (pid_output);
}

void FlowcellTemp_Init()
{
	Max31865_init(&pt100, &hspi3, MAX_CS_GPIO_Port, MAX_CS_Pin, 2, 50);
	FlowcellTemp_OFF();
}

void FlowcellTemp_ON()
{
	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
	__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_1, 0);
	
	TempControl_Running = true;
}

void FlowcellTemp_OFF()
{
	TempControl_Running = false;

	__HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_1, 0);
  HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1);
	sum_err = 0.0f;
}

void UpdateTemperature()
{
		float pt100Temp;
	if (Max31865_readTemp(&pt100, &pt100Temp)) {
		last_temp = flowcell_temp;
		flowcell_temp = pt100Temp;
	}
}

void CalcAndUpdatePWMValue()
{
  __HAL_TIM_SetCompare(&htim3, TIM_CHANNEL_1, CalcTempPID());
}