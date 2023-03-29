#define SERIAL_BAUDRATE 115200
#define SPI_SPEED 1000000

//To change once mounted on the roof
#define NORTH_AZ_ENCODER_OFFSET_VAL = 0

// Lower to 3° later
#define ZENITH_SAFETY_MARGIN_DEG = 5.0

// temp because elev encoder is not working
#define ELEV_INIT_POSITION_DEG = 90.0 - ZENITH_SAFETY_MARGIN_DEG

// plus-minus (nearly) 2 turns
#define AZ_MAX_ROTATION_DEG = 360 + 350

#define HWSerial Serial2

#define ENCODERS_SPI SPI

#define ZERO 0x00

#define ENCODERS_MAX pow(2,20) - 1
#define HYSTERISIS 70

#define REDUC_AZ = 200
#define REDUC_ELEV = 140

#define STEP_PER_TURN = 200

/*

#define ENCODERS_SPEED 10000

#define MICROSTEPS 25600.0
#define ALT_REDUCTION 40.0

#define HOME_AZ 123456
#define ZENITH 123456

*/

#define STEP_DURATION_AZ_MS 400
#define STEP_DURATION_ELEV_MS 100

#define High(pin) digitalWriteFast(pin, HIGH)
#define Low(pin) digitalWriteFast(pin, LOW)

#define STEPPER_ELEV_ENABLE_PIN 21
#define STEPPER_ELEV_DIR_PIN 22
#define STEPPER_ELEV_STEP_PIN 23
#define STEPPER_ELEV_BOOST_PIN 20
#define STEPPER_ELEV_FAULT_PIN 19

#define ENCODER_ELEV_NCS_PIN 15


#define STEPPER_AZ_ENABLE_PIN 2
#define STEPPER_AZ_DIR_PIN 3
#define STEPPER_AZ_STEP_PIN 4
#define STEPPER_AZ_BOOST_PIN 1
#define STEPPER_AZ_FAULT_PIN 0

#define ENCODER_AZ_NCS_PIN 10


#define LED_On digitalWriteFast(LED_BUILTIN, HIGH);
#define LED_Off digitalWriteFast(LED_BUILTIN, LOW);