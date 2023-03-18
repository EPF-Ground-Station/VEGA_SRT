#ifndef ANTENNA_H
#define ANTENNA_H

#include <SPI.h>

#include "define.h"

#include "Stepper.h"
#include "Encoder.h"

class Antenna {

    private:

    Stepper *stepper_az;
    Encoder *encoder_az;

    Stepper *stepper_alt;
    Encoder *encoder_alt;

    public:

    Antenna(){

        stepper_az = new Stepper(
            STEPPER_AZ_ENABLE_PIN,
            STEPPER_AZ_DIR_PIN,
            STEPPER_AZ_STEP_PIN,
            STEPPER_AZ_BOOST_PIN,
            STEPPER_AZ_FAULT_PIN,
            STEP_DURATION_AZ_MS);

        stepper_alt = new Stepper(
            STEPPER_ALT_ENABLE_PIN,
            STEPPER_ALT_DIR_PIN,
            STEPPER_ALT_STEP_PIN,
            STEPPER_ALT_BOOST_PIN,
            STEPPER_ALT_FAULT_PIN,
            STEP_DURATION_ALT_MS);

        ENCODERS_SPI.begin();
        ENCODERS_SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));

        encoder_az = new Encoder(
            ENCODERS_SPI, 
            ENCODER_AZ_NCS_PIN);

        encoder_alt = new Encoder(
            ENCODERS_SPI,
            ENCODER_ALT_NCS_PIN);

    }

    ~Antenna(){

        delete(stepper_az);
        delete(stepper_alt);

        delete(encoder_az);
        delete(encoder_alt);
    }

    void go_home(){

        //TODO define HOME
        point_to(0,0);
    }

    void empty_water(){
        
    }

    void point_to(float az, float alt){

        AzRef = az * ENCODERS_MAX / 360.0;
        AltRef = alt * ENCODERS_MAX / 360.0;

    }

};

#endif