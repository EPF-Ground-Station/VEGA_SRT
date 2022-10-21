#include <TimeLib.h>
#include "define.h"

int AltCurrentDirection = 0, AzCurrentDirection = 0;
int AltDirectionToGo = 0, AzDirectionToGo = 0;
float max_encoders = pow(2,20) - 1;
uint32_t AltRef = 0, AzRef = 0;
uint32_t AltDiff = 0, AzDiff = 0;
uint32_t AltSteps = 0, AzSteps = 0;
uint32_t AzEncPos = 500, AltEncPos = 500;
uint32_t AzEncPosAbs = 0, AltEncPosAbs = 0;
uint32_t AzEncPosInit = 0, AltEncPosInit = 0;
uint16_t AzEncMultiTurn = 0;
uint16_t AzEncMultiTurnAbs = 0;
uint16_t AzEncMultiTurnInit = 0;
uint8_t AzEncCRC = 0, AltEncCRC = 0;
bool AltEncError = 0 , AzEncError = 0 , AltEncWarning = 0 , AzEncWarning = 0;
uint8_t point_counter = 0;
int32_t counter_test_2 = 0;
//uint32_t AltPointsCoordinates [7] = {25000, 4000, 0, 21000, 25000, 28000, 20000};
//uint32_t AzPointsCoordinates [7] = {40000, 45000, 0, 1036000, 1010000, 992000, 975000};
uint32_t AltPointsCoordinates [2] = {0, 95000};
uint32_t AzPointsCoordinates [2] = {200, 475000};


char sat_name[25];
char TLE1[70];
char TLE2[70];

void setup(){
    init_pins();
    Serial.begin(9600);
    while (!Serial && millis() < 4000);
    setSyncProvider(getTeensy3Time);

    AzNCSon;
    AltNCSon;
    AzSCKoff;
    AltSCKoff;
    delayMicroseconds(5);

    AzENABLEon;
    AltENABLEon;
    AzDIRon;
    AltDIRon;

    init_encoders_abs();

    Timer_StepOn_Az.begin(StepOn_Az, STEP_SPEED_AZ);
    Timer_StepsOff_Az.begin(StepOff_Az);
    Timer_StepOn_Alt.begin(StepOn_Alt, STEP_SPEED_ALT);
    Timer_StepsOff_Alt.begin(StepOff_Alt);
    
    Timer_Encoders.begin(Encoders, ENCODERS_SPEED);
}

void loop(){

//    sat_tracker();

//    test1();
    test2();

}
