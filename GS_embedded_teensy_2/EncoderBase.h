#ifndef ENCODER_BASE_H
#define ENCODER_BASE_H

#include "define.h"
#include "Error.h"

class EncoderBase {

    protected:

    int n_cs_pin = -1;

    SPIClass *spi;

    uint32_t  pos_dec = 0;

    public:

    EncoderBase(SPIClass &spi, int n_cs_pin):n_cs_pin(n_cs_pin){

        this->spi = &spi;

        pinMode(n_cs_pin, OUTPUT);
    }

    ~EncoderBase(){
        
    }

    // TODO ADD ERROR HANDLING TO AVOID RETURNING WRONG VALUES

    ErrorStatus get_encoder_pos_value(uint32_t & value){
        
        ErrorStatus error = read_values();

        if(error.type == ErrorType::NONE){
            value = pos_dec;
        }

        return error;
    }

    protected :

    virtual ErrorStatus read_values(uint32_t & value) = 0;

};

#endif