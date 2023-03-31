#define SERIAL_BAUDRATE 115200

#define SPI_SPEED 1000000

//To change once mounted on the roof
#define NORTH_AZ_ENCODER_OFFSET_VAL 0

//To measure more precisely ?
#define ZENITH_ELEV_ENCODER_OFFSET_VAL 727780

#define ZENITH_SAFETY_MARGIN_DEG 3.0

// plus-minus (nearly) 2 turns
#define AZ_MAX_ROTATION_DEG (360 + 350)

#define HWSerial Serial

#define ENCODERS_SPI SPI

#define ZERO 0x00

#define ENCODERS_MAX pow(2,20) - 1

//unit, not used for the moment ???
#define HYSTERISIS 70

#define REDUC_AZ 200
#define REDUC_ELEV 140

#define AZ_MICRO_STEP_PER_TURN 12800
#define ELEV_MICRO_STEP_PER_TURN 25600

#define STEP_PERIOD_AZ_uS 20
#define STEP_PERIOD_ELEV_uS 30

#define High(pin) digitalWrite(pin, HIGH)
#define Low(pin) digitalWrite(pin, LOW)

#define STEPPER_ELEV_STEP_PIN 25
#define STEPPER_ELEV_DIR_PIN 26
#define STEPPER_ELEV_ENABLE_PIN 27
#define STEPPER_ELEV_BOOST_PIN 14
#define STEPPER_ELEV_FAULT_PIN 12

#define ENCODER_ELEV_NCS_PIN 21


#define STEPPER_AZ_STEP_PIN 17
#define STEPPER_AZ_DIR_PIN 16
#define STEPPER_AZ_ENABLE_PIN 4
#define STEPPER_AZ_BOOST_PIN 2
#define STEPPER_AZ_FAULT_PIN 15

#define ENCODER_AZ_NCS_PIN 22

#define LED_On digitalWrite(LED_BUILTIN, HIGH);
#define LED_Off digitalWrite(LED_BUILTIN, LOW);