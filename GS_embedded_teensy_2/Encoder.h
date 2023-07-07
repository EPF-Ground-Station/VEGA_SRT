#ifndef ENCODER_H
#define ENCODER_H

#include "define.h"
#include "EncoderBase.h"

class Encoder : public EncoderBase {

    public:

    Encoder(SPIClass &spi, int n_cs_pin, std::string name) : EncoderBase(spi, n_cs_pin, name) {}

    // TODO check CRC ?

    private :

    ErrorStatus read_values(){

        //HWSerial.println("DEBUG enter read_values");

        Low(n_cs_pin);

        delayMicroseconds(10);

        uint32_t second_word = spi->transfer16(ZERO);
        uint32_t third_word = spi->transfer16(ZERO);

        High(n_cs_pin);

        //WSerial.println("DEBUG got data from SPI");

        uint32_t mask = 1;

        uint32_t warning_bit = (third_word >> 8) & mask;
        uint32_t error_bit = (third_word >> 9) & mask;

        //HWSerial.println("DEBUG computed errors bits");

        if(error_bit == 0){

            std::string error_msg = name + " encoder error bit";
            ErrorStatus status(ErrorType::ERROR, error_msg);
            return status;
        }

        pos_dec = (second_word << 4) + (third_word >> 12);

        if(warning_bit == 0){

            std::string warning_msg = name + " encoder warning bit";
            ErrorStatus status(ErrorType::WARNING, warning_msg);
            return status;
        }

        ErrorStatus status(ErrorType::NONE, "");
        //HWSerial.println("DEBUG end of read values");
        return status;
    }

};

#endif
