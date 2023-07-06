#ifndef ANTENNA_POINTING_MECHANISM_H
#define ANTENNA_POINTING_MECHANISM_H

#include <SPI.h>

#include "define.h"

#include "Stepper.h"
#include "Encoder.h"
#include "EncoderMultiTurn.h"

class AntennaPointingMechanism {

    private:

    //static to be accessed from timer ISR
    static Stepper *az_stepper; // = nullptr;
    static int az_twice_step_count;//= 0;
    static hw_timer_t *az_stepper_timer; // = nullptr;
    EncoderMultiTurn *az_encoder = nullptr;

    //static to be accessed from timer ISR
    static Stepper *elev_stepper;// = nullptr;
    static int elev_twice_step_count;// = 0;
    static hw_timer_t *elev_stepper_timer;// = nullptr;
    Encoder *elev_encoder = nullptr;

    int az_init_turn_count;

    public:

    //TODO make singleton ?
    AntennaPointingMechanism(){

        az_stepper = new Stepper(
            AZ_STEPPER_STEP_PIN,
            AZ_STEPPER_DIR_PIN,
            AZ_STEPPER_ENABLE_PIN,
            AZ_STEPPER_BOOST_PIN,
            AZ_STEPPER_FAULT_PIN,
            AZ_STEP_PERIOD_uS,
            0);

        elev_stepper = new Stepper(
            ELEV_STEPPER_STEP_PIN,
            ELEV_STEPPER_DIR_PIN,
            ELEV_STEPPER_ENABLE_PIN,
            ELEV_STEPPER_BOOST_PIN,
            ELEV_STEPPER_FAULT_PIN,
            ELEV_STEP_PERIOD_uS,
            1);

        ENCODERS_SPI.begin();
        ENCODERS_SPI.beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE1));

        az_encoder = new EncoderMultiTurn(
            ENCODERS_SPI, 
            AZ_ENCODER_NCS_PIN,
            "Az");

        elev_encoder = new Encoder(
            ENCODERS_SPI,
            ELEV_ENCODER_NCS_PIN,
            "Elev");


        // read some values to clean the SPI bus    
        for(int i = 0; i < 10; i++){
            int value;
            az_encoder->get_encoder_pos_value(value);
            delay(50);
            elev_encoder->get_encoder_pos_value(value);
            delay(50);
        }
        // safety check assume the antenna won't do a full turn on az when disconnected
        // also assume : 0 << init turn count << Max Turn Count, so the encoder turn counter won't under/overflow

        //TODO not sure how to handle errors here
        ErrorStatus status = az_encoder->get_turn_count(az_init_turn_count);

    }

    ~AntennaPointingMechanism(){

        delete(az_stepper);
        delete(elev_stepper);

        delete(az_encoder);
        delete(elev_encoder);
    }

    //TODO implement error report
    ErrorStatus untangle(){

        int az_current_turn_count = 0;
        
        ErrorStatus status = az_encoder->get_turn_count(az_current_turn_count);
        
        if(status.type == ErrorType::ERROR){
            return status;
        }

        // untangle the cables
        az_step((az_current_turn_count - az_init_turn_count)*AZ_MICRO_STEP_PER_TURN*AZ_REDUC);

        return status;
    }


    //TODO implement error report
    //TODO separate az and elev point_to (should be static fct ??) into helper functions for async iterative correction and separate errors

    // az and elev are in degree
    // az grow to the east (aimed at the north)
    // elev is 0° at the horizon and grow toward zenith
    ErrorStatus point_to(float az_deg, float elev_deg){

        // ------ point az ------------

        // not sure how % behave with value < 0 so convert first
        while (az_deg < 0.0){ az_deg += 360.0;}

        int az_target_encoder_val = (int)(az_deg / 360.0 * ENCODERS_MAX + AZ_NORTH_ENCODER_VAL) % ENCODERS_MAX;

        int az_current_encoder_val = 0;

        ErrorStatus statusEncoderAz = az_encoder->get_encoder_pos_value(az_current_encoder_val);

        if(statusEncoderAz.type == ErrorType::ERROR){
            return statusEncoderAz;
        }

        int az_encoder_val_diff = az_target_encoder_val - az_current_encoder_val;

        // take the shortest path

        if( abs(az_encoder_val_diff) > ENCODERS_MAX/2){

            if(az_encoder_val_diff < 0){
                az_encoder_val_diff = az_encoder_val_diff + ENCODERS_MAX;

            } else{
                az_encoder_val_diff = az_encoder_val_diff - ENCODERS_MAX;
            }
            
        }

        // predicting if next move will be too much and untangle cables first if needed

        int az_current_turn_count = 0;
        
        ErrorStatus statusAzTurnCount = az_encoder->get_turn_count(az_current_turn_count);
        
        if(statusAzTurnCount.type == ErrorType::ERROR){
            return statusAzTurnCount;
        }

        float az_pred_diff_deg_since_init = ((float)(az_current_turn_count - az_init_turn_count) + (az_current_encoder_val + az_encoder_val_diff)/ENCODERS_MAX ) * 360.0;

        int step_to_untangle = 0;
        if(az_pred_diff_deg_since_init > AZ_MAX_ROTATION_DEG){
            step_to_untangle = (-AZ_MICRO_STEP_PER_TURN*AZ_REDUC);
        }
        if(az_pred_diff_deg_since_init < -AZ_MAX_ROTATION_DEG){
            step_to_untangle = (AZ_MICRO_STEP_PER_TURN*AZ_REDUC);
        }

        int az_step_to_turn = (float)az_encoder_val_diff / ENCODERS_MAX * AZ_REDUC * AZ_MICRO_STEP_PER_TURN;

        az_step(az_step_to_turn + step_to_untangle);

        //------ point elev --------------

        // safety check

        if(elev_deg > 90.0 - ELEV_ZENITH_SAFETY_MARGIN_DEG){
            elev_deg = 90.0 - ELEV_ZENITH_SAFETY_MARGIN_DEG;
        }
        if(elev_deg < 0.0){
            elev_deg = 0.0;
        }

        // ENCODERS_MAX is added in case ELEV_ZENITH_ENCODER_VAL is less than ENCODERS_MAX/4 and the result is negative
        // when it's not the case "% ENCODERS_MAX" remove the excess turn
        const int ELEV_HORIZON_ENCODER_OFFSET_VAL = (int)(ELEV_ZENITH_ENCODER_VAL - ENCODERS_MAX/4 + ENCODERS_MAX) % ENCODERS_MAX;

        int elev_target_encoder_val = (int)(elev_deg / 360.0 * ENCODERS_MAX + ELEV_HORIZON_ENCODER_OFFSET_VAL) % ENCODERS_MAX;

        int elev_current_encoder_val = 0;

        ErrorStatus statusEncoderElev = elev_encoder->get_encoder_pos_value(elev_current_encoder_val);

        if(statusEncoderElev.type == ErrorType::ERROR){
            return statusEncoderElev;
        }

        int elev_encoder_val_diff = elev_target_encoder_val - elev_current_encoder_val;

        // take the shortest path

        if( abs(elev_encoder_val_diff) > ENCODERS_MAX/2){

            if(elev_encoder_val_diff < 0){
                elev_encoder_val_diff = elev_encoder_val_diff + ENCODERS_MAX;

            } else{
                elev_encoder_val_diff = elev_encoder_val_diff - ENCODERS_MAX;
            }
            
        }

        int elev_step_to_turn = (float)elev_encoder_val_diff / ENCODERS_MAX * ELEV_REDUC * ELEV_MICRO_STEP_PER_TURN;

        elev_step(-elev_step_to_turn);

    }

    private:


    // az timer helper function and ISR


    void az_step(int steps){
        int step_duration_factor = 1;
        if (steps < STEPS_SLOWDOWN_THRESHOLD){
            step_duration_factor = STEPS_SLOWDOWN_FACTOR;
        }
        az_twice_step_count = 2*steps;
        
        //base clock is 80MHz with a 80 prescaler a timer tick is 1 uS
        az_stepper_timer = timerBegin(az_stepper->getTimerNum(), 80, true);

        timerAttachInterrupt(az_stepper_timer, az_step_ISR, true);

        int half_step_duration_uS = az_stepper->getStepDuration()/2 * step_duration_factor;

        //true for autoreload, false for oneshot
        timerAlarmWrite(az_stepper_timer, half_step_duration_uS, false);

        timerAlarmEnable(az_stepper_timer);
    }

    static void az_step_ISR(){
        if(az_twice_step_count > 0){

            if(az_twice_step_count % 2 == 0){
                az_stepper->stepRiseEdge();
            } else {
                az_stepper->stepLowerEdge();
            }

            az_twice_step_count -= 1;

            timerAlarmEnable(az_stepper_timer);
        }
    }

    // elev timer helper function and ISR


    void elev_step(int steps){
        int step_duration_factor = 1;
        if (steps < STEPS_SLOWDOWN_THRESHOLD){
            step_duration_factor = STEPS_SLOWDOWN_FACTOR;
        }


        elev_twice_step_count = 2*steps;
        
        //base clock is 80MHz with a 80 prescaler a timer tick is 1 uS
        elev_stepper_timer = timerBegin(elev_stepper->getTimerNum(), 80, true);

        timerAttachInterrupt(elev_stepper_timer, elev_step_ISR, true);

        int half_step_duration_uS = elev_stepper->getStepDuration()/2 * step_duration_factor;

        //true for autoreload, false for oneshot
        timerAlarmWrite(elev_stepper_timer, half_step_duration_uS, false);

        timerAlarmEnable(elev_stepper_timer);
    }

    static void elev_step_ISR(){
        if(elev_twice_step_count > 0){

            if(elev_twice_step_count % 2 == 0){
                elev_stepper->stepRiseEdge();
            } else {
                elev_stepper->stepLowerEdge();
            }

            elev_twice_step_count -= 1;

            timerAlarmEnable(elev_stepper_timer);
        }
    }

};

//static to be accessed from timer ISR
Stepper *AntennaPointingMechanism::az_stepper = nullptr;
int AntennaPointingMechanism::az_twice_step_count = 0;
hw_timer_t *AntennaPointingMechanism::az_stepper_timer = nullptr; 

Stepper *AntennaPointingMechanism::elev_stepper = nullptr;
int AntennaPointingMechanism::elev_twice_step_count = 0;
hw_timer_t *AntennaPointingMechanism::elev_stepper_timer = nullptr;

#endif