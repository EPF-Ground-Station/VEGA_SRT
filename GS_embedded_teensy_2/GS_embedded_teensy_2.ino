#include "define.h"

#include "Antenna.h"

Antenna antenna;

float az, elev = 0.0;

void setup() {

    HWSerial.begin(SERIAL_BAUDRATE);

    HWSerial.println("Emptying water");

    LED_On;
    antenna.empty_water();
    LED_Off;

    HWSerial.println("Setup Finished");

}

void loop() {



    // az and elev are in degree
    // az grow to the east (aimed at the north)
    // elev is 0° at the horizon and grow toward zenith
    while (HWSerial.available() <= 0){delay(50);}
    az = HWSerial.parseFloat();
    elev = HWSerial.parseFloat();

    HWSerial.println("azimuth = " + String(az) + " elevation = " + String(elev));

    LED_On;
    antenna.point_to(az, elev);
    LED_Off;
}