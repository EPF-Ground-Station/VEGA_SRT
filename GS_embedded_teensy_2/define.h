
#define SERIAL_BAUDRATE 115200

#define SPI_SPEED 1000000

#define INACTIVITY_MAX_DURATION 61 // 61 seconds after which standby mode is enabled

//To change once mounted on the roof
// not used, replaced by set_north_offset cmd
#define AZ_NORTH_ENCODER_VAL 0

//To measure more precisely ?
#define ELEV_ZENITH_ENCODER_VAL 715671

//TODO change to 3.0
#define ELEV_ZENITH_SAFETY_MARGIN_DEG 2.0
#define ELEV_HORIZON_SAFETY_MARGIN_DEG 5.0

// plus-minus (nearly) 1.25 turns
#define AZ_MAX_ROTATION_DEG (360 + 100)

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
#define AZ_STEPPER_BOOST_PIN 15
#define AZ_STEPPER_FAULT_PIN 14

#define AZ_ENCODER_NCS_PIN 13


#define ELEV_STEPPER_STEP_PIN 32
#define ELEV_STEPPER_DIR_PIN 33
#define ELEV_STEPPER_ENABLE_PIN 25
#define ELEV_STEPPER_BOOST_PIN 26
#define ELEV_STEPPER_FAULT_PIN 27

#define ELEV_ENCODER_NCS_PIN 12

#define STEPS_SLOWDOWN_THRESHOLD 2000
#define STEPS_SLOWDOWN_FACTOR 4

#define STANDBY_ZENITH_THRESHOLD_CORRECTION_DEG (ELEV_ZENITH_SAFETY_MARGIN_DEG + 10.0)


#define LED_On digitalWrite(LED_BUILTIN, HIGH);
#define LED_Off digitalWrite(LED_BUILTIN, LOW);