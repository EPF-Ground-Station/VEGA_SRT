#ifndef ENCODER_H
#define ENCODER_H

#include "define.h"

class Encoder {

    private:

    int n_cs_pin = -1;

    SPIClass *spi;

    public:

    Encoder(SPIClass &spi, int n_cs_pin):n_cs_pin(n_cs_pin){

        this->spi = &spi;

        pinMode(n_cs_pin, OUTPUT);
    }

    ~Encoder(){
        
    }

    float get_position_deg(){

        //TODO add init pos offset to result ?

        Low(n_cs_pin);

        delayMicroseconds(10);

        uint32_t first_word = spi->transfer16(ZERO);
        uint32_t second_word = spi->transfer16(ZERO);
        uint32_t third_word = spi->transfer16(ZERO);

        High(n_cs_pin);

        uint32_t pos_dec = (second_word << 4) + (third_word >> 12);
        float pos_deg = (pos_dec * 360.0) / ENCODERS_MAX;

        return(pos_deg);
    }


};

#endif