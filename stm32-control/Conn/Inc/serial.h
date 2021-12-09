#ifndef SERIAL_H
#define SERIAL_H

void SerialConnect_Init();

void ProcessReceiveCommand();

void Send_CurrentTemperatureToPC();

void Send_CurrentValvePos();

#endif // SERIAL_H