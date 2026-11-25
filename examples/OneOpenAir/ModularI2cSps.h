#pragma once

#include <stdint.h>

// SPS30 over I2C, kept out of OneOpenAir.ino. The UART and I2C Sensirion
// drivers both declare SPS30CmdId, so they cannot be included together.
void modularI2cSpsBegin(void);
int16_t modularI2cSpsWake(void);
int16_t modularI2cSpsStart(void);
int16_t modularI2cSpsReady(uint16_t &ready);
int16_t modularI2cSpsRead(float &mc1, float &mc25, float &mc4, float &mc10, float &nc05, float &nc1,
                          float &nc25, float &nc4, float &nc10, float &typical);
int16_t modularI2cSpsStop(void);
