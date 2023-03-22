#include "TeensyTimerTool.h"
using namespace TeensyTimerTool;
#include <Sgp4.h>

#define HWSerial Serial2

#define STEP_SPEED_AZ 400
#define STEP_SPEED_ALT 100
#define ENCODERS_SPEED 10000
#define ENCODERS_MAX  pow(2,20) - 1
#define ZERO 0x00

#define MICROSTEPS 25600.0
#define ALT_REDUCTION 40.0

#define HOME_AZ 123456
#define ZENITH 123456

#define HYSTERISIS 70

#define AltENABLEPin 21
#define AltENABLEon digitalWriteFast(AltENABLEPin, HIGH)
#define AltENABLEoff digitalWriteFast(AltENABLEPin, LOW)

#define AltDIRPin 22
#define AltDIRon digitalWriteFast(AltDIRPin, HIGH)
#define AltDIRoff digitalWriteFast(AltDIRPin, LOW)

#define AltSTEPPin 23
#define AltSTEPon digitalWriteFast(AltSTEPPin, HIGH)
#define AltSTEPoff digitalWriteFast(AltSTEPPin, LOW)

#define AltBOOSTPin 20
#define AltBOOSTon digitalWriteFast(AltBOOSTPin, HIGH)
#define AltBOOSToff digitalWriteFast(AltBOOSTPin, LOW)

#define AltFAULTPin 19
#define AltFAULT digitalReadFast(AltFAULTPin)

#define AzENABLEPin 2
#define AzENABLEon digitalWriteFast(AzENABLEPin, HIGH)
#define AzENABLEoff digitalWriteFast(AzENABLEPin, LOW)

#define AzDIRPin 3
#define AzDIRon digitalWriteFast(AzDIRPin, HIGH)
#define AzDIRoff digitalWriteFast(AzDIRPin, LOW)

#define AzSTEPPin 4
#define AzSTEPon digitalWriteFast(AzSTEPPin, HIGH)
#define AzSTEPoff digitalWriteFast(AzSTEPPin, LOW)

#define AzBOOSTPin 1
#define AzBOOSTon digitalWriteFast(AzBOOSTPin, HIGH)
#define AzBOOSToff digitalWriteFast(AzBOOSTPin, LOW)

#define AzFAULTPin 0
#define AzFAULT digitalReadFast(AzFAULTPin)

// #define AzSCKPin 7
// #define AzSCKon digitalWriteFast(AzSCKPin, HIGH)
// #define AzSCKoff digitalWriteFast(AzSCKPin, LOW)

#define AzNCSPin 9 // 10 for SPI default
#define AzNCSon digitalWriteFast(AzNCSPin, HIGH)
#define AzNCSoff digitalWriteFast(AzNCSPin, LOW)

// #define AzMISOPin 9
// #define getAzMISO digitalReadFast(AzMISOPin)
// #define AzMISOisHIGH digitalReadFast(AzMISOPin)

//#define AzMOSIPin 10

#define LEDon digitalWriteFast(LED_BUILTIN, HIGH);
#define LEDoff digitalWriteFast(LED_BUILTIN, LOW);

// #define AltSCKPin 14
// #define AltSCKon digitalWriteFast(AltSCKPin, HIGH)
// #define AltSCKoff digitalWriteFast(AltSCKPin, LOW)

#define AltNCSPin 6
#define AltNCSon digitalWriteFast(AltNCSPin, HIGH)
#define AltNCSoff digitalWriteFast(AltNCSPin, LOW)

// #define AltMISOPin 16
// #define getAltMISO digitalReadFast(AltMISOPin)
// #define AltMISOisHIGH digitalReadFast(AltMISOPin)

// #define AltMOSIPin 17

PeriodicTimer Timer_StepOn_Az(TCK);
OneShotTimer Timer_StepsOff_Az(TCK);
PeriodicTimer Timer_StepOn_Alt(TCK);
OneShotTimer Timer_StepsOff_Alt(TCK);

PeriodicTimer Timer_Encoders(TCK);

Sgp4 sat;
