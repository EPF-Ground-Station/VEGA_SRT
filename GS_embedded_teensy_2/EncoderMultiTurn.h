#ifndef ENCODER_MULTITURN_H
#define ENCODER_MULTITURN_H

#include "define.h"
#include "EncoderBase.h"

class EncoderMultiTurn : public EncoderBase {

    private:

    uint32_t turn_count = -1;

    public:

    EncoderMultiTurn(SPIClass &spi, int n_cs_pin) : EncoderBase(spi, n_cs_pin) {}

    // TODO ADD ERROR HANDLING TO AVOID RETURNING WRONG VALUES

    ErrorStatus get_turn_count(uint32_t & value){

        ErrorStatus error = read_values();

        if(error.type == ErrorType::NONE){
            value = turn_count;
        }

        return error;
    }

    private :

    ErrorStatus read_values(){

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