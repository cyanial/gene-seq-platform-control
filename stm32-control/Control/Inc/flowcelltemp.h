#ifndef FLOWCELLTEMP_H
#define FLOWCELLTEMP_H

void FlowcellTemp_Init();

void FlowcellTemp_ON();

void FlowcellTemp_OFF();

void UpdateTemperature();

void CalcAndUpdatePWMValue();

#endif // FLOWCELLTEMP_H