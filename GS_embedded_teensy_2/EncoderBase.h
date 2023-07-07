#ifndef ENCODER_BASE_H
#define ENCODER_BASE_H

#include "define.h"
#include "Error.h"
#include "string"

class EncoderBase {

    protected:

    int n_cs_pin = -1;

    SPIClass *spi;

    uint32_t  pos_dec = 0;

    std::string name;

    public:

    EncoderBase(SPIClass &spi, int n_cs_pin, std::string name):
        n_cs_pin(n_cs_pin),
        name(name){

        this->spi = &spi;

        pinMode(n_cs_pin, OUTPUT);
    }

    ~EncoderBase(){
        
    }

    ErrorStatus get_encoder_pos_value(int & value){

        //HWSerial.println("DEBUG enter get_encoder_pos_value");
        
        ErrorStatus status;

        //HWSerial.println("DEBUG read values");

        int error_attempts_counter = 0;

        while(error_attempts_counter < 10){
            status = read_values();
            if(status.type == ErrorType::ERROR){
                error_attempts_counter += 1;
            } else{
                value = pos_dec;
                return status;
            }

            delay(50);
        }

        return status;
    }

    protected :

    virtual ErrorStatus read_values() = 0;

};

#endif
