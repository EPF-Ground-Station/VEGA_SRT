#ifndef ANTENNA_H
#define ANTENNA_H

#include <SPI.h>

#include "define.h"

#include "Stepper.h"
#include "Encoder.h"
#include "EncoderMultiTurn.h"

class Antenna {

    private:

    Stepper *stepper_az = nullptr;
    EncoderMultiTurn *encoder_az = nullptr;

    Stepper *stepper_elev = nullptr;
    Encoder *encoder_elev = nullptr;

    int init_az_turn_count;

    public:

    Antenna(){

        stepper_az = new Stepper(
            STEPPER_AZ_ENABLE_PIN,
            STEPPER_AZ_DIR_PIN,
            STEPPER_AZ_STEP_PIN,
            STEPPER_AZ_BOOST_PIN,
            STEPPER_AZ_FAULT_PIN,
            STEP_PERIOD_AZ_uS);

        stepper_elev = new Stepper(
            STEPPER_ELEV_ENABLE_PIN,
            STEPPER_ELEV_DIR_PIN,
            STEPPER_ELEV_STEP_PIN,
            STEPPER_ELEV_BOOST_PIN,
            STEPPER_ELEV_FAULT_PIN,
            STEP_PERIOD_ELEV_uS);

        ENCODERS_SPI.begin();
        ENCODERS_SPI.beginTransaction(SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE1));

        encoder_az = new EncoderMultiTurn(
            ENCODERS_SPI, 
            ENCODER_AZ_NCS_PIN);

        encoder_elev = new Encoder(
            ENCODERS_SPI,
            ENCODER_ELEV_NCS_PIN);

        //safety check assume the antenna won't do a full turn on az when disconnected
        init_az_turn_count = encoder_az->get_turn_count();
    }

    ~Antenna(){

        delete(stepper_az);
        delete(stepper_elev);

        delete(encoder_az);
        delete(encoder_elev);
    }

    void go_home(){

        //TODO define HOME

        int current_az_turn_count = encoder_az->get_turn_count();

        stepper_az->step((current_az_turn_count - init_az_turn_count)*AZ_MICRO_STEP_PER_TURN*REDUC_AZ);

        point_to(0, 90.0 - ZENITH_SAFETY_MARGIN_DEG);

    }

    void empty_water(){

        point_to(0, 60);

        delay(5000);

        go_home();
        
    }

    void point_to(float az_deg, float elev_deg){

        // ------ point az ------------

        int target_az_encoder_val = (az_deg / 360.0 * ENCODERS_MAX + NORTH_AZ_ENCODER_OFFSET_VAL) % ENCODERS_MAX;

        int current_az_encoder_val = encoder_az->get_encoder_pos_value();

        int az_encoder_val_diff = target_az_encoder_val - current_az_encoder_val;

        if( abs(az_encoder_val_diff) > ENCODERS_MAX/2){

            if(az_encoder_val_diff < 0){
                az_encoder_val_diff = az_encoder_val_diff + ENCODERS_MAX;

            } else{
                az_encoder_val_diff = az_encoder_val_diff - ENCODERS_MAX;
            }
            
        }

        int current_az_turn_count = encoder_az->get_turn_count();

        float pred_diff_deg_since_init = ((float)(current_az_turn_count - init_az_turn_count) + (current_az_encoder_val + az_encoder_val_diff)/ENCODERS_MAX ) * 360.0;

        if(pred_diff_deg_since_init > AZ_MAX_ROTATION_DEG){
            stepper_az->step_backward(AZ_MICRO_STEP_PER_TURN*REDUC_AZ);
        }
        if(pred_diff_deg_since_init < AZ_MAX_ROTATION_DEG){
            stepper_az->step_forward(AZ_MICRO_STEP_PER_TURN*REDUC_AZ);
        }

        int step_to_turn = az_encoder_val_diff / ENCODERS_MAX * REDUC_AZ * AZ_MICRO_STEP_PER_TURN;

        stepper_az->step(step_to_turn);

        // TODO optional recheck encoder value

        //------ point elev --------------

        if(elev > 90.0 - ZENITH_SAFETY_MARGIN_DEG){
            elev = ZENITH_SAFETY_MARGIN_DEG
        }
        if(elev < 0.0){
            elev = 0.0;
        }

        float current_pos_deg = ELEV_INIT_POSITION_DEG - stepper_elev->get_steps_count()/ELEV_MICRO_STEP_PER_TURN/REDUC_ELEV;

        float pos_diff = elev - current_pos_deg;

        stepper_elev->step(-pos_diff*ELEV_MICRO_STEP_PER_TURN*REDUC_ELEV);
    }

};

#endif