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

    while (HWSerial.available() <= 0){delay(50);}
    az = HWSerial.parseFloat();
    elev = HWSerial.parseFloat();

    HWSerial.println("azimuth = " + String(az) + " elevation = " + String(elev));

    antenna.point_to(az, elev);
}