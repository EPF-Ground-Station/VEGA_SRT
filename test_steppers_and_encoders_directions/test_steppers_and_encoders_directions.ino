#include <SPI.h>

#define HWSerial Serial

#define ENCODERS_MAX pow(2, 20) - 1

#define ZERO 0x00

#define STEP_DURATION_AZ_MS 20
#define STEP_DURATION_ALT_MS 30

//#define High(pin) digitalWriteFast(pin, HIGH)
//#define Low(pin) digitalWriteFast(pin, LOW)
#define High(pin) digitalWrite(pin, HIGH)
#define Low(pin) digitalWrite(pin, LOW)

//#define High(pin) GPIO.out_w1ts = ((uint32_t)1 << pin);
//#define Low(pin) GPIO.out_w1tc = ((uint32_t)1 << pin);

#define STEPPER_ALT_STEP_PIN 25
#define STEPPER_ALT_DIR_PIN 26
#define STEPPER_ALT_ENABLE_PIN 27
#define STEPPER_ALT_BOOST_PIN 14
#define STEPPER_ALT_FAULT_PIN 12

#define ENCODER_ALT_NCS_PIN 21

#define STEPPER_AZ_STEP_PIN 17
#define STEPPER_AZ_DIR_PIN 16
#define STEPPER_AZ_ENABLE_PIN 4
#define STEPPER_AZ_BOOST_PIN 0
#define STEPPER_AZ_FAULT_PIN 2

#define ENCODER_AZ_NCS_PIN 22

void setup()
{

    SPI.begin();
    SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));

    HWSerial.begin(115200);

    HWSerial.println("hello");
    // init az

    pinMode(STEPPER_AZ_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_AZ_DIR_PIN, OUTPUT);
    pinMode(STEPPER_AZ_STEP_PIN, OUTPUT);
    pinMode(STEPPER_AZ_BOOST_PIN, OUTPUT);
    pinMode(STEPPER_AZ_FAULT_PIN, INPUT_PULLUP);

    High(STEPPER_AZ_ENABLE_PIN);
    High(STEPPER_AZ_DIR_PIN);

    pinMode(ENCODER_AZ_NCS_PIN, OUTPUT);
    High(ENCODER_AZ_NCS_PIN);

    // init alt

    pinMode(STEPPER_ALT_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_ALT_DIR_PIN, OUTPUT);
    pinMode(STEPPER_ALT_STEP_PIN, OUTPUT);
    pinMode(STEPPER_ALT_BOOST_PIN, OUTPUT);
    pinMode(STEPPER_ALT_FAULT_PIN, INPUT_PULLUP);

    High(STEPPER_ALT_ENABLE_PIN);
    High(STEPPER_ALT_DIR_PIN);

    pinMode(ENCODER_ALT_NCS_PIN, OUTPUT);
    High(ENCODER_ALT_NCS_PIN);


    

    // HWSerial.println("begin turn forward az");

    // for (int i = 0; i < 200*200*40; i++)
    // {
    //     step_forward_az();
    // }

    // HWSerial.println("finished turn forward az");

    HWSerial.println("begin quarter turn forward alt");

    for (int i = 0; i < 140*25600/4; i++)
    {
        step_forward_alt();
    }

    HWSerial.println("finished quarter turn forward alt");
}

int i = 0;

void loop()
{
    // encoders_print();
    // delay(500);


    // step_forward_alt();
    // i++;

    // if( (i % 100) == 0){
    //     HWSerial.println(i);
    // }
}

// todo draft:
// 16 first bits are for multi-turn counter
// 20 first bits are for angular position

void encoders_print()
{

    //-------- AZ -------------

    Low(ENCODER_AZ_NCS_PIN);

    delayMicroseconds(10);

    uint32_t first_word = SPI.transfer16(ZERO);
    uint32_t second_word = SPI.transfer16(ZERO);
    uint32_t third_word = SPI.transfer16(ZERO);

    High(ENCODER_AZ_NCS_PIN);

    uint32_t pos_dec = (second_word << 4) + (third_word >> 12);
    float pos_deg = (pos_dec * 360.0) / ENCODERS_MAX;

    HWSerial.print("az encoder deg ");
    HWSerial.println(pos_deg);
    HWSerial.print("az encoder turn counter (first word) ");
    HWSerial.println(first_word);

    //-------------- ALT ------------

    Low(ENCODER_ALT_NCS_PIN);

    delayMicroseconds(10);

    second_word = SPI.transfer16(ZERO);
    third_word = SPI.transfer16(ZERO);

    High(ENCODER_ALT_NCS_PIN);

    pos_dec = (second_word << 4) + (third_word >> 12);
    pos_deg = (pos_dec * 360.0) / ENCODERS_MAX;

    HWSerial.print("alt encoder deg ");
    HWSerial.println(pos_deg);
}

void step_forward_az()
{

    High(STEPPER_AZ_STEP_PIN);
    delayMicroseconds(STEP_DURATION_AZ_MS / 2);
    Low(STEPPER_AZ_STEP_PIN);
    delayMicroseconds(STEP_DURATION_AZ_MS / 2);
}

void step_forward_alt()
{

    High(STEPPER_ALT_STEP_PIN);
    delayMicroseconds(STEP_DURATION_ALT_MS / 2);
    Low(STEPPER_ALT_STEP_PIN);
    delayMicroseconds(STEP_DURATION_ALT_MS / 2);
}
