#include <SPI.h>

#define HWSerial Serial2

#define ENCODERS_MAX pow(2, 20) - 1

#define ZERO 0x00

#define STEP_DURATION_AZ_MS 400
#define STEP_DURATION_ALT_MS 100

#define High(pin) digitalWriteFast(pin, HIGH)
#define Low(pin) digitalWriteFast(pin, LOW)

#define STEPPER_ALT_ENABLE_PIN 21
#define STEPPER_ALT_DIR_PIN 22
#define STEPPER_ALT_STEP_PIN 23
#define STEPPER_ALT_BOOST_PIN 20
#define STEPPER_ALT_FAULT_PIN 19

#define ENCODER_ALT_NCS_PIN 15

#define STEPPER_AZ_ENABLE_PIN 2
#define STEPPER_AZ_DIR_PIN 3
#define STEPPER_AZ_STEP_PIN 4
#define STEPPER_AZ_BOOST_PIN 1
#define STEPPER_AZ_FAULT_PIN 0

#define ENCODER_AZ_NCS_PIN 10

void setup()
{
    HWSerial.begin(115200);
    // init az

    pinMode(STEPPER_AZ_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_AZ_DIR_PIN, OUTPUT);
    pinMode(STEPPER_AZ_STEP_PIN, OUTPUT);
    pinMode(STEPPER_AZ_BOOST_PIN, OUTPUT);
    pinMode(STEPPER_AZ_FAULT_PIN, INPUT_PULLUP);

    High(STEPPER_AZ_ENABLE_PIN);
    High(STEPPER_AZ_DIR_PIN);

    pinMode(ENCODER_AZ_NCS_PIN, OUTPUT);

    // init alt

    pinMode(STEPPER_ALT_ENABLE_PIN, OUTPUT);
    pinMode(STEPPER_ALT_DIR_PIN, OUTPUT);
    pinMode(STEPPER_ALT_STEP_PIN, OUTPUT);
    pinMode(STEPPER_ALT_BOOST_PIN, OUTPUT);
    pinMode(STEPPER_ALT_FAULT_PIN, INPUT_PULLUP);

    High(STEPPER_ALT_ENABLE_PIN);
    High(STEPPER_ALT_DIR_PIN);

    pinMode(ENCODER_ALT_NCS_PIN, OUTPUT);

    for (int i = 0; i < 200; i++)
    {
        HWSerial.println("TODO delete");
        step_forward_az();
    }

    for (int i = 0; i < 200; i++)
    {
        step_forward_alt();
    }
}

void loop()
{
    // put your main code here, to run repeatedly:
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

    first_word = SPI.transfer16(ZERO);
    second_word = SPI.transfer16(ZERO);
    third_word = SPI.transfer16(ZERO);

    High(ENCODER_ALT_NCS_PIN);

    pos_dec = (second_word << 4) + (third_word >> 12);
    pos_deg = (pos_dec * 360.0) / ENCODERS_MAX;

    HWSerial.print("alt encoder deg ");
    HWSerial.println(pos_deg);
    HWSerial.print("alt encoder first word (also turn counter ?)");
    HWSerial.println(first_word);
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
    delay(STEP_DURATION_ALT_MS * 1000 / 2);
    Low(STEPPER_ALT_STEP_PIN);
    delay(STEP_DURATION_ALT_MS / 2);
}