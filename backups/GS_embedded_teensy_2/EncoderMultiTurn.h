#ifndef ENCODER_MULTITURN_H
#define ENCODER_MULTITURN_H

#include "define.h"
#include "EncoderBase.h"

class EncoderMultiTurn : public EncoderBase {

    private:

    uint32_t turn_count = -1;

    public:

    EncoderMultiTurn(SPIClass &spi, int n_cs_pin, std::string name) : EncoderBase(spi, n_cs_pin, name) {}

    // TODO check CRC ?

    ErrorStatus get_turn_count(int & value){

        ErrorStatus status;

        int error_attempts_counter = 0;

        while(error_attempts_counter < 10){
            status = read_values();
            if(status.type == ErrorType::ERROR){
                error_attempts_counter += 1;
            } else{
                value = turn_count;
                return status;
            }

            delay(50);
        }

        return status;
    }

    private :

    ErrorStatus read_values(){

        Low(n_cs_pin);

        delayMicroseconds(10);

        uint32_t first_word = spi->transfer16(ZERO);
        uint32_t second_word = spi->transfer16(ZERO);
        uint32_t third_word = spi->transfer16(ZERO);

        High(n_cs_pin);

        uint32_t mask = 1;

        uint32_t warning_bit = (third_word >> 8) & mask;
        uint32_t error_bit = (third_word >> 9) & mask;

        if(error_bit == 0){

            std::string error_msg = name + " encoder error bit";
            ErrorStatus status(ErrorType::ERROR, error_msg);
            return status;
        }

        pos_dec = (second_word << 4) + (third_word >> 12);

        turn_count = first_word;

        if(warning_bit == 0){

            std::string warning_msg = name + " encoder warning bit";
            ErrorStatus status(ErrorType::WARNING, warning_msg);
            return status;
        }

        ErrorStatus status(ErrorType::NONE, "");
        return status;
    }

};

#endif
