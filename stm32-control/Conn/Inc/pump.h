#ifndef PUMP_H
#define PUMP_H

#include <stdint.h>

void Pump_Init();
void Pump_MoveToPos(uint8_t pos);
void Pump_RequestValvePos();
void Pump_RequestPumpPos();
void Pump_RequestPumpState();
void Pump_PulluL(uint16_t uL);
void Pump_PushuL(uint16_t uL);

void ProcessPumpMsg();

#endif // PUMP_H