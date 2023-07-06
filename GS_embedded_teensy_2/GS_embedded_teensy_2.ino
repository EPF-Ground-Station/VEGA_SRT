#include "define.h"

#include "AntennaPointingMechanism.h"

AntennaPointingMechanism *apm = nullptr;

float az, elev = 0.0;

void setup() {
    
    HWSerial.begin(SERIAL_BAUDRATE);

    // constructor cannot be called before setup because it uses pins
    apm = new AntennaPointingMechanism();

    LED_On;
    //antenna->empty_water();
    LED_Off;

    //flush serial
    while (HWSerial.available() > 0){
        HWSerial.read();
    }

}

void loop() {

    // az and elev are in degree
    // az grow to the east (aimed at the north)
    // elev is 0° at the horizon and grow toward zenith
    while (HWSerial.available() <= 0){
        delay(50);
    }
    az = HWSerial.parseFloat();
    elev = HWSerial.parseFloat();

    //flush serial
    while (HWSerial.available() > 0){
        HWSerial.read();
    }

    HWSerial.println("Got az : " + String(az) + " elev : " + String(elev));

    // TODO change led to be used with timers
    LED_On;
    apm->point_to(az, elev);
    LED_Off;

    HWSerial.println("Finished pointing");
}