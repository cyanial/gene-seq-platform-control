#ifndef VALVE_H
#define VALVE_H

#include <stdint.h>

void VALVE_Init();
void VALVE_MoveToPos(uint8_t pos);
void VALVE_RequestPos();

void ProcessValveMsg();

#endif // VALVE_H