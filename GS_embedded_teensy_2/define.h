#define SERIAL_BAUDRATE 115200

#define SPI_SPEED 1000000

//To change once mounted on the roof
#define AZ_NORTH_ENCODER_OFFSET_VAL 0

//To measure more precisely ?
#define ELEV_ZENITH_ENCODER_OFFSET_VAL 727780

#define ELEV_ZENITH_SAFETY_MARGIN_DEG 3.0

// plus-minus (nearly) 2 turns
#define AZ_MAX_ROTATION_DEG (360 + 350)

#define HWSerial Serial

#define ENCODERS_SPI SPI

#define ZERO 0x00

#define ENCODERS_MAX (int)(pow(2,20) - 1)

//unit, not used for the moment ???
#define HYSTERISIS 70

#define AZ_REDUC 200
#define ELEV_REDUC 140

#define AZ_MICRO_STEP_PER_TURN 12800
#define ELEV_MICRO_STEP_PER_TURN 25600

#define AZ_STEP_PERIOD_uS 20
#define ELEV_STEP_PERIOD_uS 30

#define High(pin) digitalWrite(pin, HIGH)
#define Low(pin) digitalWrite(pin, LOW)

#define AZ_STEPPER_STEP_PIN 17
#define AZ_STEPPER_DIR_PIN 16
#define AZ_STEPPER_ENABLE_PIN 4
#define AZ_STEPPER_BOOST_PIN 2
#define AZ_STEPPER_FAULT_PIN 15

#define AZ_ENCODER_NCS_PIN 22


#define ELEV_STEPPER_STEP_PIN 25
#define ELEV_STEPPER_DIR_PIN 26
#define ELEV_STEPPER_ENABLE_PIN 27
#define ELEV_STEPPER_BOOST_PIN 14
#define ELEV_STEPPER_FAULT_PIN 12

#define ELEV_ENCODER_NCS_PIN 21


#define LED_On digitalWrite(LED_BUILTIN, HIGH);
#define LED_Off digitalWrite(LED_BUILTIN, LOW);