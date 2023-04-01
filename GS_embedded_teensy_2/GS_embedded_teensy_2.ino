#include "define.h"

#include "Antenna.h"

Antenna antenna;

float az, elev = 0.0;

void setup() {

    HWSerial.begin(SERIAL_BAUDRATE);

    HWSerial.println("Emptying water");

    antenna.empty_water();

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

    antenna.point_to(az, elev);
}