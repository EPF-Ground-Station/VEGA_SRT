#ifndef ENCODER_H
#define ENCODER_H

#include "define.h"

class Encoder {

    private:

    int n_cs_pin = -1;

    SPIClass *spi;

    uint32_t turn_count = -1;
    uint32_t  pos_dec = 0;

    public:

    Encoder(SPIClass &spi, int n_cs_pin):n_cs_pin(n_cs_pin){

        this->spi = &spi;

        pinMode(n_cs_pin, OUTPUT);
    }

    ~Encoder(){
        
    }

    // ADD ERROR HANDLING TO AVOID RETURNING WRONG VALUES

    uint32_t get_encoder_pos_value(){
        
        read_values();

        return pos_dec;
    }

    uint32_t get_turn_count(){

        read_values();

        return turn_count;
    }

    private :

    void read_values(){

        Low(n_cs_pin);

        delayMicroseconds(10);

        uint32_t first_word = spi->transfer16(ZERO);
        uint32_t second_word = spi->transfer16(ZERO);
        uint32_t third_word = spi->transfer16(ZERO);

        High(n_cs_pin);

        pos_dec = (second_word << 4) + (third_word >> 12);

        turn_count = first_word;
    }

};

#endif