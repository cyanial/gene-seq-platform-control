// SY01-30-M02-1
// Travel Range : 30 mm
// Step         : 12000
// Volume       : 2.5 ml
///////////////////////////////
// Valve Type   : M02
//------------ -------------- -------------- --------------
//            |      |       |      |       |       |      |
//            |      |       |      |       |       |      |
// 1 ----- 2  |  1 ---    2  |  1 -----  2  |  1    --- 2  |
//     |      |      |       |              |       |      |
//     |      |      |       |              |       |      |
//     C      |      C       |      C       |       C      |
//            |              |              |              |
//------------ -------------- -------------- --------------
// Volume Calc:
// 2.5 ml = 2,500 ul
// 30 mm = 12,000 steps
// 2,500 ul / 12,000 steps ~= 0.20833 ul / step
// 12,000 steps / 2,500 ul = 4.8 steps / ul

// Running Commands:
//   B0     B1      B2      B3 B4        B5      B6 B7
//  STX    ADDR    FUNC    PARAMS        ETX    Checksum
//   CC     00      00     0-7 | 8-15    DD     Low | High
// 
// Reponsed:
// B2 - Status

#include <stdbool.h>
#include <stdint.h>

#include "pump.h"
#include "usart.h"

#define StepsPeruL 4.8

//                          B0    B1    B2    B3    B4    B5    B6    B7
static uint8_t tx_buf[] = {0xcc, 0x00, 0x00, 0x00, 0x00, 0xdd, 0x00, 0x00}; 
static uint8_t rx_buf[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

uint8_t pump_valve_pos = 0;
uint8_t pump_pos_l = 0;
uint8_t pump_pos_h = 0;
uint8_t pump_state = 0;


bool request_valve_pos = false;
bool request_pump_pos = false;
bool request_pump_state = false;


static void SetTxCheckSum()
{
	uint16_t checksum = 0;
	for (int i = 0; i < 6; i++) {
		checksum += tx_buf[i];
	}
	
	tx_buf[6] = (uint8_t) (checksum & 0x00ff);
	tx_buf[7] = (uint8_t) (checksum >> 8);
}

// UP
static void Pump_RunClockwise(uint16_t steps)
{
	tx_buf[2] = 0x42;
	tx_buf[3] = (uint8_t) (steps & 0x00ff);
	tx_buf[4] = (uint8_t) (steps >> 8);
	SetTxCheckSum();
	HAL_UART_Transmit(&huart4, tx_buf, sizeof(tx_buf), 0xff);
}

// DOWN
static void Pump_RunCounterClockwise(uint16_t steps)
{
	tx_buf[2] = 0x43;
	tx_buf[3] = (uint8_t) (steps & 0x00ff);
	tx_buf[4] = (uint8_t) (steps >> 8);
	SetTxCheckSum();
	HAL_UART_Transmit(&huart4, tx_buf, sizeof(tx_buf), 0xff);
}

void Pump_Init()
{
	HAL_UART_Receive_DMA(&huart4, rx_buf, sizeof(rx_buf));
}

void Pump_MoveToPos(uint8_t pos)
{
	tx_buf[2] = 0x44;
	tx_buf[3] = pos;
	tx_buf[4] = 0x00;
	SetTxCheckSum();
	HAL_UART_Transmit(&huart4, tx_buf, sizeof(tx_buf), 0xff);
}

void Pump_RequestValvePos()
{
	tx_buf[2] = 0xae;
	tx_buf[3] = 0x00;
	tx_buf[4] = 0x00;
	SetTxCheckSum();
	HAL_UART_Transmit(&huart4, tx_buf, sizeof(tx_buf), 0xff);
	request_valve_pos = true;
}

void Pump_RequestPumpPos()
{
	tx_buf[2] = 0x66;
	tx_buf[3] = 0x00;
	tx_buf[4] = 0x00;
	SetTxCheckSum();
	HAL_UART_Transmit(&huart4, tx_buf, sizeof(tx_buf), 0xff);
	request_pump_pos = true;
}

void Pump_RequestPumpState()
{
	tx_buf[2] = 0x4a;
	tx_buf[3] = 0x00;
	tx_buf[4] = 0x00;
	SetTxCheckSum();
	HAL_UART_Transmit(&huart4, tx_buf, sizeof(tx_buf), 0xff);
	request_pump_state = true;
}

void Pump_PulluL(uint16_t uL)
{
	Pump_RunCounterClockwise((uint16_t)(uL*StepsPeruL));
}

void Pump_PushuL(uint16_t uL)
{
	Pump_RunClockwise((uint16_t)(uL*StepsPeruL));
}

void ProcessPumpMsg()
{
	if (request_valve_pos) {
		request_valve_pos = false;
		pump_valve_pos = rx_buf[3];
		return;
	}
	if (request_pump_pos) {
		request_pump_pos = false;
		pump_pos_l = rx_buf[3];
		pump_pos_h = rx_buf[4];
		return;
	}
	if (request_pump_state) {
		request_pump_state = false;
		pump_state = rx_buf[2];
		return;
	}
}
