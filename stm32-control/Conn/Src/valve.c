// QHF-SV06-X-T10-K1.2-S
//   X     - 
//   T10   - 10 Channels
//   K1.2  -
//   S     -
//
// Running Commands:
//   B0     B1      B2      B3 B4        B5      B6 B7
//  STX    ADDR    FUNC    PARAMS        ETX    Checksum
//   CC     00      00     0-7 | 8-15    DD     Low | High
// 
// Reponsed:
// B2 - Status

#include <stdint.h>
#include <stdbool.h>

#include "usart.h"
#include "valve.h"


//                          B0    B1    B2    B3    B4    B5    B6    B7
static uint8_t tx_buf[] = {0xcc, 0x00, 0x00, 0x00, 0x00, 0xdd, 0x00, 0x00}; 
static uint8_t rx_buf[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};

uint8_t valve_pos = 0;
// bool valve_motor_idle = true;

bool Ready_ValveMsg = true;
bool request_pos = false;
// bool request_motor = false;


static void SetTxCheckSum()
{
	uint16_t checksum = 0;
	for (int i = 0; i < 6; i++) {
		checksum += tx_buf[i];
	}
	
	tx_buf[6] = (uint8_t) (checksum & 0x00ff);
	tx_buf[7] = (uint8_t) (checksum >> 8);
}

//static bool VerifyRxCheckSum()
//{
//	uint16_t checksum = 0;
//	for (int i = 0; i < 6; i++) {
//		checksum += rx_buf[i];
//	}
//	
//	if (rx_buf[6] == (checksum & 0x00ff) && rx_buf[7] == (checksum >> 8)) {
//		return true;
//	}
//	
//	return false;
//}

void VALVE_Init()
{
	HAL_UART_Receive_DMA(&huart5, rx_buf, sizeof(rx_buf));
}

void VALVE_MoveToPos(uint8_t pos)
{
	tx_buf[2] = 0x44;
	tx_buf[3] = pos;
	tx_buf[4] = 0x00;
	
	SetTxCheckSum();
	HAL_UART_Transmit(&huart5, tx_buf, sizeof(tx_buf), 0xff);
}
void VALVE_RequestPos()
{
	tx_buf[2] = 0x3e;
	tx_buf[3] = 0x00;
	tx_buf[4] = 0x00;
	SetTxCheckSum();
	HAL_UART_Transmit(&huart5, tx_buf, sizeof(tx_buf), 0xff);
	request_pos = true;
}

//void VALVE_RequestMotor()
//{
//	tx_buf[2] = 0x4a;
//	tx_buf[3] = 0x00;
//	tx_buf[4] = 0x00;
//	SetTxCheckSum();
//	HAL_UART_Transmit(&huart5, tx_buf, sizeof(tx_buf), 0xff);
//	request_motor = true;
//}

void ProcessValveMsg()
{
	if (request_pos) {
		request_pos = false;
		valve_pos = rx_buf[3];
		return;
	}
//	if (request_motor) {
//		request_motor = false;
//		valve_motor_idle = (rx_buf[3] == 0x00);
//		return;
//	}
}
