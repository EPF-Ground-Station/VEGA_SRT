#include <TimeLib.h>
#include <Sgp4.h>

#include <cstdio>

#include "define.h"

#include "Antenna.h"

char sat_name[SAT_NAME_STRING_MAX_LENGTH];
char tle_line1[TLE_LINE_STRING_MAX_LENGTH];
char tle_line2[TLE_LINE_STRING_MAX_LENGTH];

Sgp4 sat_tracker;

Antenna* antenna = nullptr;

void setup() {

    HWSerial.begin(SERIAL_BAUDRATE);
    HWSerial.println("Starting setup");

    //------ only for debug remove later ---------
    const char test_sat_name[] = "ISS (ZARYA)";
    const char test_tle_line1[] = "1 25544U 98067A   16065.25775256 -.00164574  00000-0 -25195-2 0  9990";
    const char test_tle_line2[] = "2 25544  51.6436 216.3171 0002750 185.0333 238.0864 15.54246933988812";

    snprintf (sat_name, SAT_NAME_MAX_LENGTH, "%s", test_sat_name);
    snprintf (tle_line1, TLE_LINE_MAX_LENGTH, "%s", test_tle_line1);
    snprintf (tle_line2, TLE_LINE_MAX_LENGTH, "%s", test_tle_line2);
    //--------------------------------------------

    //HWSerial.println("Enter TLE");
    //while(!HWSerial.available()){}
    //read_from_serial();

    setSyncProvider(getTeensyTime);

    sat_tracker.site(POS_LATITUDE, POS_LONGITUDE, POS_ALTITUDE);
    sat_tracker.init(sat_name, tle_line1, tle_line2);

    antenna = new Antenna();

    antenna->empty_water();

    HWSerial.println("Finished setup");

}

void loop() {

    if(HWSerial.available()){
        read_from_serial();
        sat_tracker.init(sat_name, tle_line1, tle_line2);
    }

    // (unsigned long)now() - 7199 ???
    sat_tracker.findsat( (unsigned long)now() );

    HWSerial.println("azimuth = " + String(sat_tracker.satAz) + " elevation = " + String(sat_tracker.satEl) + " distance = " + String(sat_tracker.satDist));

    antenna->point_to(sat_tracker.satAz, sat_tracker.satAz);

    delay(1000/UPDATE_FREQ_HZ);
}

void read_from_serial(){

    for(int i = 0; i < SAT_NAME_STRING_MAX_LENGTH-1; i++){
        sat_name[i] = (char) Serial.read();
    }
    sat_name[SAT_NAME_STRING_MAX_LENGTH] = "\0";

    HWSerial.read();

    for(int i = 0; i < TLE_LINE_STRING_MAX_LENGTH-1; i++){
        tle_line1[i] = (char) Serial.read();
    }
    tle_line1[TLE_LINE_STRING_MAX_LENGTH] = "\0";
    
    HWSerial.read();

    for(int i = 0; i < TLE_LINE_STRING_MAX_LENGTH-1; i++){
        tle_line2[i] = (char) Serial.read();
    }
    tle_line2[TLE_LINE_STRING_MAX_LENGTH] = "\0";

    HWSerial.read();
}