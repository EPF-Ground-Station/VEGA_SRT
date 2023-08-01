#ifndef ANTENNA_POINTING_MECHANISM_H
#define ANTENNA_POINTING_MECHANISM_H

#include <SPI.h>

#include "define.h"

#include "Stepper.h"
#include "Encoder.h"
#include "EncoderMultiTurn.h"
    

/*
TODO helper functions

move steppers
deg from encoder

shortest rotation given encoder val diff
point north w/o untangle (so point north can be used in constructor before init turn count)
*/

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
        //TODO should point to north first (using shorted rotation) before getting init turn count ? (to avoid the case where north is on 40th turn 1° and antenna start on 39th turn 359° then think untangling to north is on 39th turn 1°)
        int current_turn_count;
        int current_az_encoder_val;

        ErrorStatus status = az_encoder->get_turn_count(current_turn_count);

        //tmp fix :( requirement manual check on power on
        if(status.type == ErrorType::ERROR){
            HWSerial.println("Error initializing turn count in constructor");
            HWSerial.println(status.msg.c_str());
        }

        status = az_encoder->get_encoder_pos_value(current_az_encoder_val);
        //tmp fix :( requirement manual check on power on
        if(status.type == ErrorType::ERROR){
            HWSerial.println("Error initializing turn count in constructor");
            HWSerial.println(status.msg.c_str());
        }

        //HWSerial.println("DEBUG current_turn_count" + String(current_turn_count));
        //HWSerial.println("DEBUG current_az_encoder_val" + String(current_az_encoder_val));

        az_init_turn_count = current_turn_count;
        
        if(current_az_encoder_val > ENCODERS_MAX/2){
            az_init_turn_count += 1;
        }

        //HWSerial.println("DEBUG az_init_turn_count" + String(az_init_turn_count));

        
        //HWSerial.println("DEBUG got init turn count");


    }

    ~AntennaPointingMechanism(){

        delete(az_stepper);
        delete(elev_stepper);

        delete(az_encoder);
        delete(elev_encoder);
    }

    ErrorStatus getCurrentAz(float& az_deg){

        int az_current;
        ErrorStatus status = az_encoder->get_encoder_pos_value(az_current);

        az_deg = (az_current - north_encoder_offset) * 360/ENCODERS_MAX;
        
        while (az_deg > 360){az_deg -= 360;}
        
        //az_deg %= 360;
        return status;
    }

    ErrorStatus getCurrentAlt(float& alt_deg){

        int alt_current;
        ErrorStatus status = elev_encoder->get_encoder_pos_value(alt_current);

        const int ELEV_HORIZON_ENCODER_OFFSET_VAL = (int)(ELEV_ZENITH_ENCODER_VAL - ENCODERS_MAX/4 + ENCODERS_MAX) % ENCODERS_MAX;
        // int elev_target_encoder_val = (int)(elev_deg / 360.0 * ENCODERS_MAX + ELEV_HORIZON_ENCODER_OFFSET_VAL) % ENCODERS_MAX;
        alt_deg = (alt_current - ELEV_HORIZON_ENCODER_OFFSET_VAL)*360/ENCODERS_MAX;
        while (alt_deg > 90){alt_deg -= 90;}

        return status;
    }


    ErrorStatus untangle_north(){

        //HWSerial.println("DEBUG called untangle_north ");

        standByDisable();

        int az_current_turn_count = 0;
        
        ErrorStatus status = az_encoder->get_turn_count(az_current_turn_count);

        //HWSerial.println("DEBUG az turn count " + String(az_current_turn_count));
        
        if(status.type == ErrorType::ERROR){
            return status;
        }

        int az_current_pos = 0;
        status = az_encoder->get_encoder_pos_value(az_current_pos);

        //HWSerial.println("DEBUG az encoder pos " + String(az_current_pos));

        if(status.type == ErrorType::ERROR){
            return status;
        }

        // untangle the cables (compute diff from initial north position)
        int az_steps = (( (float)(az_init_turn_count - az_current_turn_count) + (float)((int)north_encoder_offset - az_current_pos)/(float)ENCODERS_MAX )*AZ_MICRO_STEP_PER_TURN*AZ_REDUC);
        if(az_steps > 0){
            az_stepper->setDirection(Stepper::Direction::Forward);
        }else{
            az_stepper->setDirection(Stepper::Direction::Backward);
        }

        az_steps = abs(az_steps);

        //HWSerial.println("DEBUG az duration step " + String(az_stepper->getStepDuration()/2));
        //HWSerial.println("DEBUG az steps abs " + String(az_steps));

        for(int i = 0; i < az_steps; i++){
            az_stepper->stepRiseEdge();
            delayMicroseconds(az_stepper->getStepDuration()/2);
            az_stepper->stepLowerEdge();
            delayMicroseconds(az_stepper->getStepDuration()/2);
        }

        //TODO only last status is reported (warning from get turn count won't show)
        return status;
    }

    ErrorStatus point_zenith(){

        standByDisable();

        ErrorStatus status;

        int elev_current_pos = 0;
        status = elev_encoder->get_encoder_pos_value(elev_current_pos);

        if(status.type == ErrorType::ERROR){
            return status;
        }

        int safe_zenith_encoder_val = (int)(ELEV_ZENITH_ENCODER_VAL - ELEV_ZENITH_SAFETY_MARGIN_DEG/360.0*ENCODERS_MAX + ENCODERS_MAX) % ENCODERS_MAX;
        int elev_encoder_val_diff = safe_zenith_encoder_val - elev_current_pos;

        // take the shortest path

        if( abs(elev_encoder_val_diff) > ENCODERS_MAX/2){

            if(elev_encoder_val_diff < 0){
                elev_encoder_val_diff = elev_encoder_val_diff + ENCODERS_MAX;

            } else{
                elev_encoder_val_diff = elev_encoder_val_diff - ENCODERS_MAX;
            }
            
        }

        int elev_steps = -(( (float)elev_encoder_val_diff/(float)ENCODERS_MAX )*ELEV_MICRO_STEP_PER_TURN*ELEV_REDUC);

        if(elev_steps > 0){
            elev_stepper->setDirection(Stepper::Direction::Forward);
        }else{
            elev_stepper->setDirection(Stepper::Direction::Backward);
        }

        elev_steps = abs(elev_steps);

        for(int i = 0; i < elev_steps; i++){
            elev_stepper->stepRiseEdge();
            delayMicroseconds(elev_stepper->getStepDuration()/2);
            elev_stepper->stepLowerEdge();
            delayMicroseconds(elev_stepper->getStepDuration()/2);
        }

        return status;
    }

    // az and elev are in degree
    // az grow to the east (aimed at the north)
    // elev is 0° at the horizon and grow toward zenith
    ErrorStatus point_to(float az_deg, float elev_deg){

        standByDisable();

        ErrorStatus status;

        // ------ compute steps az ------------

        // not sure how % behave with value < 0 so convert first
        while (az_deg < 0.0){ az_deg += 360.0;}

        int az_target_encoder_val = (int)(az_deg / 360.0 * ENCODERS_MAX + (int)north_encoder_offset) % ENCODERS_MAX;

        int az_current_encoder_val = 0;

        status = az_encoder->get_encoder_pos_value(az_current_encoder_val);

        //HWSerial.println("DEBUG az encoder pos " + String(az_current_encoder_val));

        if(status.type == ErrorType::ERROR){
            return status;
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
        
        status = az_encoder->get_turn_count(az_current_turn_count);

        //HWSerial.println("DEBUG az turn count " + String(az_current_turn_count));
        
        if(status.type == ErrorType::ERROR){
            return status;
        }

        float az_pred_diff_deg_since_init = ((float)(az_current_turn_count - az_init_turn_count) + (float)(az_current_encoder_val + az_encoder_val_diff - (int)north_encoder_offset)/ENCODERS_MAX ) * 360.0;


        float test_var = (float)(az_current_encoder_val + az_encoder_val_diff - (int)north_encoder_offset)/ENCODERS_MAX;
        //HWSerial.println("DEBUG az_current_encoder_val " + String(az_current_encoder_val));
        //HWSerial.println("DEBUG az_encoder_val_diff " + String(az_encoder_val_diff));
        //HWSerial.println("DEBUG test_var " + String(test_var));
        //HWSerial.println("DEBUG az_current_turn_count " + String(az_current_turn_count));
        //HWSerial.println("DEBUG az_init_turn_count " + String(az_init_turn_count));
        //HWSerial.println("DEBUG az_pred_diff_deg_since_init " + String(az_pred_diff_deg_since_init));

        int step_to_untangle = 0;
        if(az_pred_diff_deg_since_init > AZ_MAX_ROTATION_DEG){
            step_to_untangle = (-AZ_MICRO_STEP_PER_TURN*AZ_REDUC);
        }
        if(az_pred_diff_deg_since_init < -AZ_MAX_ROTATION_DEG){
            step_to_untangle = (AZ_MICRO_STEP_PER_TURN*AZ_REDUC);
        }

        int az_step_to_turn = (float)az_encoder_val_diff / ENCODERS_MAX * AZ_REDUC * AZ_MICRO_STEP_PER_TURN;


        //HWSerial.println("DEBUG az az_step_to_turn " + String(az_step_to_turn));
        //HWSerial.println("DEBUG az step_to_untangle pos " + String(step_to_untangle));


        int az_step_to_turn_total = az_step_to_turn + step_to_untangle;

        //------ compute steps elev --------------

        // safety check

        //TODO add warning when unreachable
        if(elev_deg > 90.0 - ELEV_ZENITH_SAFETY_MARGIN_DEG){
            elev_deg = 90.0 - ELEV_ZENITH_SAFETY_MARGIN_DEG;
        }
        if(elev_deg < 0.0 + (ELEV_HORIZON_SAFETY_MARGIN_DEG) ){
            elev_deg = 0.0 + ELEV_HORIZON_SAFETY_MARGIN_DEG;
        }

        // ENCODERS_MAX is added in case ELEV_ZENITH_ENCODER_VAL is less than ENCODERS_MAX/4 and the result is negative
        // when it's not the case "% ENCODERS_MAX" remove the excess turn
        const int ELEV_HORIZON_ENCODER_OFFSET_VAL = (int)(ELEV_ZENITH_ENCODER_VAL - ENCODERS_MAX/4 + ENCODERS_MAX) % ENCODERS_MAX;

        int elev_target_encoder_val = (int)(elev_deg / 360.0 * ENCODERS_MAX + ELEV_HORIZON_ENCODER_OFFSET_VAL) % ENCODERS_MAX;

        int elev_current_encoder_val = 0;

        status = elev_encoder->get_encoder_pos_value(elev_current_encoder_val);

        //HWSerial.println("DEBUG elev encoder val" + String(elev_current_encoder_val));


        if(status.type == ErrorType::ERROR){
            return status;
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

        //HWSerial.println("DEBUG elev steps" + String(elev_step_to_turn_total));
        //HWSerial.println("DEBUG az steps" + String(az_step_to_turn_total));


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

        az_step_to_turn_total = abs(az_step_to_turn_total);
        elev_step_to_turn_total = abs(elev_step_to_turn_total);

        int az_step_duration = az_stepper->getStepDuration();
        if (abs(az_step_to_turn_total) < STEPS_SLOWDOWN_THRESHOLD && az_step_to_turn_total != 0){
            az_step_duration *= STEPS_SLOWDOWN_FACTOR;
        }

        int elev_step_duration = elev_stepper->getStepDuration();
        if (abs(elev_step_to_turn_total) < STEPS_SLOWDOWN_THRESHOLD && elev_step_to_turn_total != 0){
            elev_step_duration *= STEPS_SLOWDOWN_FACTOR;
        }

        //HWSerial.println("DEBUG  elev_step_duration " + String(elev_step_duration));
        //HWSerial.println("DEBUG  az_step_duration " + String(az_step_duration));

        int max_step_count = max (az_step_to_turn_total, elev_step_to_turn_total);
        int min_step_count = min (az_step_to_turn_total, elev_step_to_turn_total);
        int max_step_duration = max (az_step_duration, elev_step_duration);

        int second_part_duration = elev_step_duration;
        if(az_step_to_turn_total > elev_step_to_turn_total){
            second_part_duration = az_step_duration;
        }

        

        // first run the common steps then the other at the max speed (usefull when one has a lot of steps and not the other)
        for (int j = 0; j < min_step_count; j++) {

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
        //HWSerial.println("DEBUG start part 2 steps for loop");
        for (int j = 0; j < (max_step_count - min_step_count); j++) {

            if(az_step_to_turn_total > 0){
              az_stepper->stepRiseEdge();
              az_step_to_turn_total--;
            }
            if(elev_step_to_turn_total > 0){
              elev_stepper->stepRiseEdge();
              elev_step_to_turn_total--;
            }
            delayMicroseconds(second_part_duration / 2);
            az_stepper->stepLowerEdge();
            elev_stepper->stepLowerEdge();
            delayMicroseconds(second_part_duration / 2);
        }

        //TODO any other warning than the last will be lost
        return status;

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

            //check elev and repoint to zenith if needed
            int elev_current_pos = 0;
            ErrorStatus elev_status = elev_encoder->get_encoder_pos_value(elev_current_pos);

            if(elev_status.type != ErrorType::ERROR){
                int elev_encoder_val_diff = ELEV_ZENITH_ENCODER_VAL - elev_current_pos;
                //I think it work with the current setup but it should compute the shortest path to take into account the case were 0 of the encoder is ~ at 45°
                if((float)abs(elev_encoder_val_diff)/(float)ENCODERS_MAX * 360.0 > STANDBY_ZENITH_THRESHOLD_CORRECTION_DEG){
                    elev_status = point_zenith();
                }
            }

                
            //check az and untangle if needed
            int az_current_turn_count = 0;
        
            ErrorStatus status_untangle = az_encoder->get_turn_count(az_current_turn_count);

            if(status_untangle.type != ErrorType::ERROR){

                int az_current_pos = 0;
                status_untangle = az_encoder->get_encoder_pos_value(az_current_pos);

                if(status_untangle.type != ErrorType::ERROR){
                    int az_deg_diff = (( (float)(az_init_turn_count - az_current_turn_count) + (float)((int)north_encoder_offset - az_current_pos)/(float)ENCODERS_MAX )*360.0);
                
                    if(abs(az_deg_diff) > AZ_MAX_ROTATION_DEG){
                        status_untangle = untangle_north();
                    }
                }
            }

            standbyEnable(); //redisable steppers after update

            if (status_untangle.type == ErrorType::ERROR && elev_status.type == ErrorType::ERROR){
                return ErrorStatus(ErrorType::ERROR, status_untangle.msg + " " + elev_status.msg);
            } else if(status_untangle.type == ErrorType::ERROR){
                return status_untangle;
            } else{
                return elev_status;
            }
        }

        return status;
    }

    void setNorthOffset(unsigned new_offset){
        if(north_encoder_offset <= ENCODERS_MAX/2 && new_offset > ENCODERS_MAX/2){
            az_init_turn_count -= 1;
            //HWSerial.println("DEBUG init_turn_count - 1");
        }
        else if(north_encoder_offset > ENCODERS_MAX/2 && new_offset <= ENCODERS_MAX/2){
            az_init_turn_count += 1;
            //HWSerial.println("DEBUG init_turn_count + 1");
        }

        north_encoder_offset = new_offset;
    }
        
};

#endif
