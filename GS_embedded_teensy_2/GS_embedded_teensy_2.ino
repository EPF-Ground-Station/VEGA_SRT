#include "define.h"

#include "Antenna.h"

Antenna *antenna = nullptr;

float az, elev = 0.0;

void setup() {
    
    HWSerial.begin(SERIAL_BAUDRATE);

    // constructor cannot be called before setup because it uses pins
    antenna = new Antenna();

    LED_On;
    antenna->empty_water();
    LED_Off;

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

    LED_On;
    antenna->point_to(az, elev);
    LED_Off;
}