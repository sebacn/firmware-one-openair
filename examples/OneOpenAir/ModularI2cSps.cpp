#include "ModularI2cSps.h"

#if defined(AG_MODULAR_I2C)
#include <SensirionI2cSps30.h>
#include <Wire.h>

static SensirionI2cSps30 modularI2cSps;

void modularI2cSpsBegin(void) {
  modularI2cSps.begin(Wire, SPS30_I2C_ADDR_69);
}

int16_t modularI2cSpsWake(void) {
  return modularI2cSps.wakeUpSequence();
}

int16_t modularI2cSpsStart(void) {
  return modularI2cSps.startMeasurement(SPS30_OUTPUT_FORMAT_OUTPUT_FORMAT_FLOAT);
}

int16_t modularI2cSpsReady(uint16_t &ready) {
  return modularI2cSps.readDataReadyFlag(ready);
}

int16_t modularI2cSpsRead(float &mc1, float &mc25, float &mc4, float &mc10, float &nc05, float &nc1,
                          float &nc25, float &nc4, float &nc10, float &typical) {
  return modularI2cSps.readMeasurementValuesFloat(mc1, mc25, mc4, mc10, nc05, nc1, nc25, nc4, nc10,
                                                   typical);
}

int16_t modularI2cSpsStop(void) {
  return modularI2cSps.stopMeasurement();
}
#endif
