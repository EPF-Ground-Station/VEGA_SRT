#ifndef ENCODER_H
#define ENCODER_H

#include "define.h"
#include "EncoderBase.h"

class Encoder : public EncoderBase {

    public:

    Encoder(SPIClass &spi, int n_cs_pin) : EncoderBase(spi, n_cs_pin) {}

    // TODO ADD ERROR HANDLING TO AVOID RETURNING WRONG VALUES

    private :

    void read_values(){

        Low(n_cs_pin);

        delayMicroseconds(10);

        uint32_t second_word = spi->transfer16(ZERO);
        uint32_t third_word = spi->transfer16(ZERO);

        High(n_cs_pin);

        pos_dec = (second_word << 4) + (third_word >> 12);
    }

};

#endif