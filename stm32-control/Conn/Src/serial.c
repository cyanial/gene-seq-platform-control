#include <stdint.h>
#include <stdbool.h>

#include "serial.h"
#include "usart.h"
#include "main.h"
#include "flowcelltemp.h"

bool Ready_PCCommand = false;

extern float flowcell_temp;
extern float setup_temp;

// User-defined protocol STM32 UART <---> PC 
// B0(STX): 0x55 | (B1)ETX: 0xaa
// B1 (Device ID) : 0x00 - TempControl 
//                  0x01 - Pump
//                  0x02 - Valve
// B2 (Message Type) : 
//   Flowcell       B1 = 0x00
//                    0x00 - Send Current Temperature  (TX)
//                    0x01 - Send setpoint temperature (TX)
//                    0x01 - Set setpoint temperature  (RX)
//                    0x02 - Turn ON PID Control       (RX)
//                    0x03 - Turn OFF PID Control      (RX)
//
//   Pump           B1 = 0x01
//                    0x00 - Set Valve Position        (RX)
//                    0x01 - Pull xxxx ul              (RX)
//                    0x02 - Push xxxx ul              (RX)
//
//   Valve          B1 = 0x02
//                    0x00 - Set Valve Position        (RX)
//  
// 
//                
//                      B0    B1    B2    B3    B4    B5
uint8_t tx_buf_pc[] = {0x55, 0x00, 0x00, 0x00, 0x00, 0xaa};
uint8_t rx_buf_pc[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0xaa};


void SerialConnect_Init()
{
	HAL_UART_Receive_DMA(&huart1, rx_buf_pc, sizeof(rx_buf_pc));
}

void ProcessReceiveCommand()
{
	if ((rx_buf_pc[0] == 0x55) && (rx_buf_pc[5] == 0xaa)) {
		
		/* Temperature Control Block */
		if (rx_buf_pc[1] == 0x00) {
			if (rx_buf_pc[2] == 0x01) {
				// Setpoint temperature
				setup_temp = (float) (rx_buf_pc[3] * 1.0f + rx_buf_pc[4] * 1.0f / 100.0f);
			}
			
			if (rx_buf_pc[2] == 0x02) {
				// Turn on PID Control
				FlowcellTemp_ON();
			}
			
			if (rx_buf_pc[2] == 0x03) {
				// Turn off PID Control
				FlowcellTemp_OFF();
			}
			
			return;
		}
		
		/* Pump Control Block */
		if (rx_buf_pc[1] == 0x01) {
			
			return;
		}
		
		/* Valve Control Block */
		if (rx_buf_pc[1] == 0x02) {
			return;
		}
	}
}

void Send_CurrentTemperatureToPC()
{
	uint16_t temp = (uint16_t) (flowcell_temp * 100);
	
	tx_buf_pc[3] = (uint8_t) (temp / 100);
	tx_buf_pc[4] = (uint8_t) (temp % 100);
	
	HAL_UART_Transmit(&huart1, tx_buf_pc, sizeof(tx_buf_pc), 0xff);
	
}

// Receive - Callback
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if (huart->Instance == USART1) {
		Ready_PCCommand = true;
	}
}