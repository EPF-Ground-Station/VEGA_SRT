#ifndef ANTENNA_POINTING_MECHANISM_H
#define ANTENNA_POINTING_MECHANISM_H

#include <SPI.h>

#include "define.h"

#include "Stepper.h"
#include "Encoder.h"
#include "EncoderMultiTurn.h"
    

class AntennaPointingMechanism {

    enum class Mode { ACTIVE, STANDBY };

    private:

    Mode currentMode = Mode::ACTIVE;

    Stepper *az_stepper = nullptr;
    EncoderMultiTurn *az_encoder = nullptr;

    Stepper *elev_stepper = nullptr;
    Encoder *elev_encoder = nullptr;

    int az_init_turn_count;

    unsigned north_encoder_offset = 0;

    public:

    //TODO make singleton ?
    AntennaPointingMechanism(){

        //HWSerial.println("DEBUG enter constructor");

        az_stepper = new Stepper(
            AZ_STEPPER_STEP_PIN,
            AZ_STEPPER_DIR_PIN,
            AZ_STEPPER_ENABLE_PIN,
            AZ_STEPPER_BOOST_PIN,
            AZ_STEPPER_FAULT_PIN,
            AZ_STEP_PERIOD_uS
            );

        //HWSerial.println("DEBUG enter init az stepper success");

        elev_stepper = new Stepper(
            ELEV_STEPPER_STEP_PIN,
            ELEV_STEPPER_DIR_PIN,
            ELEV_STEPPER_ENABLE_PIN,
            ELEV_STEPPER_BOOST_PIN,
            ELEV_STEPPER_FAULT_PIN,
            ELEV_STEP_PERIOD_uS
            );
        
        //HWSerial.println("DEBUG enter init elev stepper success");


        ENCODERS_SPI.begin();
        ENCODERS_SPI.beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE1));

        az_encoder = new EncoderMultiTurn(
            ENCODERS_SPI, 
            AZ_ENCODER_NCS_PIN,
            "Az");

        //HWSerial.println("DEBUG enter init az encoder success");


        elev_encoder = new Encoder(
            ENCODERS_SPI,
            ELEV_ENCODER_NCS_PIN,
            "Elev");
            
        //HWSerial.println("DEBUG enter init elev encoder success");


        // read some values to clean the SPI bus    
        for(int i = 0; i < 10; i++){
            int value;
            az_encoder->get_encoder_pos_value(value);
            delay(50);
            elev_encoder->get_encoder_pos_value(value);
            delay(50);
        }
        
        //HWSerial.println("DEBUG flushed SPI");

        // safety check assume the antenna won't do a full turn on az when disconnected
        // also assume : 0 << init turn count << Max Turn Count, so the encoder turn counter won't under/overflow

        //TODO not sure how to handle errors here
        ErrorStatus status = az_encoder->get_turn_count(az_init_turn_count);
        //tmp fix :(
        if(status.type == ErrorType::ERROR){
            HWSerial.println("Error initializing turn count");
        }
        //HWSerial.println("DEBUG got init turn count");


    }

    ~AntennaPointingMechanism(){

        delete(az_stepper);
        delete(elev_stepper);

        delete(az_encoder);
        delete(elev_encoder);
    }

    ErrorStatus untangle_north(){

        standByDisable();

        int az_current_turn_count = 0;
        
        ErrorStatus status = az_encoder->get_turn_count(az_current_turn_count);
        
        if(status.type == ErrorType::ERROR){
            return status;
        }

        int az_current_pos = 0;
        status = az_encoder->get_encoder_pos_value(az_current_pos);

        if(status.type == ErrorType::ERROR){
            return status;
        }

        // untangle the cables (compute diff from initial north position)
        int az_steps = (( (float)az_init_turn_count + (float)north_encoder_offset/(float)ENCODERS_MAX - (float)az_current_turn_count - (float)az_current_pos/(float)ENCODERS_MAX)*AZ_MICRO_STEP_PER_TURN*AZ_REDUC);
        if(az_steps > 0){
            az_stepper->setDirection(Stepper::Direction::Forward);
        }else{
            az_stepper->setDirection(Stepper::Direction::Backward);
        }
        for(int i = 0, i < az_steps, i++){
            az_stepper->stepRiseEdge();
            delay(az_stepper->getStepDuration()/2);
            az_stepper->stepLowerEdge();
            delay(az_stepper->getStepDuration()/2);
        }

        //TODO only last status is reported (warning from get turn count won't show)
        return status;
    }

    ErrorStatus point_zenith(){

        standByDisable();

        int elev_current_pos = 0;
        status = elev_encoder->get_encoder_pos_value(elev_current_pos);

        if(status.type == ErrorType::ERROR){
            return status;
        }

        int elev_steps = (( )*ELEV_MICRO_STEP_PER_TURN*ELEV_REDUC);
        if(elev_steps > 0){
            elev_stepper->setDirection(Stepper::Direction::Forward);
        }else{
            elev_stepper->setDirection(Stepper::Direction::Backward);
        }
        for(int i = 0, i < az_steps, i++){
            elev_stepper->stepRiseEdge();
            delay(elev_stepper->getStepDuration()/2);
            elev_stepper->stepLowerEdge();
            delay(elev_stepper->getStepDuration()/2);
        }

        return status;
    }

    // az and elev are in degree
    // az grow to the east (aimed at the north)
    // elev is 0° at the horizon and grow toward zenith
    ErrorStatus point_to(float az_deg, float elev_deg){

        standByDisable();

        // ------ compute steps az ------------

        // not sure how % behave with value < 0 so convert first
        while (az_deg < 0.0){ az_deg += 360.0;}

        // TODO use configurable offset
        int az_target_encoder_val = (int)(az_deg / 360.0 * ENCODERS_MAX + north_encoder_offset) % ENCODERS_MAX;

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

        int az_step_to_turn_total = az_step_to_turn + step_to_untangle;

        //------ compute steps elev --------------

        // safety check

        //TODO add warning when unreachable
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

        int elev_step_to_turn_total = -elev_step_to_turn;


        // --------------- turn the steppers ---------

        if(az_step_to_turn_total > 0){
            az_stepper->setDirection(Stepper::Direction::Forward);
        }else{
            az_stepper->setDirection(Stepper::Direction::Backward);
        }

        if(elev_step_to_turn_total > 0){
            elev_stepper->setDirection(Stepper::Direction::Forward);
        }else{
            elev_stepper->setDirection(Stepper::Direction::Backward);
        }


        int az_step_duration = az_stepper->getStepDuration();
        if (abs(az_step_to_turn_total) < STEPS_SLOWDOWN_THRESHOLD && az_step_to_turn_total != 0){
            az_step_duration *= STEPS_SLOWDOWN_FACTOR;
        }

        int elev_step_duration = elev_stepper->getStepDuration();
        if (abs(elev_step_to_turn_total) < STEPS_SLOWDOWN_THRESHOLD && elev_step_to_turn_total != 0){
            elev_step_duration *= STEPS_SLOWDOWN_FACTOR;
        }

        int max_step_count = max (az_step_to_turn_total, elev_step_to_turn_total);
        int max_step_duration = max (az_step_duration, elev_step_duration);

        //TODO speed up in second part if one stepper is doing way more than the other
        for (int j = 0; j < max_step_count; j++) {

            if(az_step_to_turn_total > 0){
              az_stepper->stepRiseEdge();
              az_step_to_turn_total--;
            }
            if(elev_step_to_turn_total > 0){
              elev_stepper->stepRiseEdge();
              elev_step_to_turn_total--;
            }
            delayMicroseconds(max_step_duration / 2);
            az_stepper->stepLowerEdge();
            elev_stepper->stepLowerEdge();
            delayMicroseconds(max_step_duration / 2);
        }

        //TODO return status

    }

    void standbyEnable(){
        currentMode = Mode::STANDBY;
        az_stepper->disable();
        elev_stepper->disable();
    }

    void standByDisable(){
        currentMode = Mode::ACTIVE;
        az_stepper->enable();
        elev_stepper->enable();
    }

    //TODO finish and error handling
    ErrorStatus standByUpdate(){
        ErrorStatus status = ErrorStatus(ErrorType::NONE, "");

        if(currentMode == Mode::STANDBY){

            //if elev diff > threshold point to zenith and north
            ErrorStatus status_untangle = untangle();

            standbyEnable(); //redisable steppers after update
        }
    }

    void setNorthOffset(unsigned offset){
        north_encoder_offset = offset;
    }
        
};

#endif
