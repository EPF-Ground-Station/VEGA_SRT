#include "define.h"

#include "Antenna.h"

Antenna antenna;

float az, elev = 0.0;

void setup() {

    HWSerial.begin(SERIAL_BAUDRATE);
    HWSerial.println("Starting setup");

    antenna.empty_water();

    HWSerial.println("Finished setup");

}

void loop() {

    while (HWSerial.available() <= 0){delay(50)}

    HWSerial.println("azimuth = " + String(az) + " elevation = " + String(elev));

    antenna.point_to(az, elev);
}