#ifndef ENCODER_BASE_H
#define ENCODER_BASE_H

#include "define.h"

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

    uint32_t get_encoder_pos_value(){
        
        read_values();

        return pos_dec;
    }

    protected :

    virtual void read_values() = 0;

};

#endif