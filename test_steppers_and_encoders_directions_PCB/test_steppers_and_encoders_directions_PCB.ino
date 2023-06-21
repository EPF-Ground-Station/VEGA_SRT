#include <SPI.h>

#define HWSerial Serial

#define SERIAL_BAUDRATE 115200


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

#define LED_On digitalWrite(LED_BUILTIN, HIGH);
#define LED_Off digitalWrite(LED_BUILTIN, LOW);


#define STEPPER_ALT_STEP_PIN 32
#define STEPPER_ALT_DIR_PIN 33
#define STEPPER_ALT_ENABLE_PIN 25
#define STEPPER_ALT_BOOST_PIN 26
#define STEPPER_ALT_FAULT_PIN 27

#define ENCODER_ALT_NCS_PIN 12

#define STEPPER_AZ_STEP_PIN 17
#define STEPPER_AZ_DIR_PIN 16
#define STEPPER_AZ_ENABLE_PIN 4
#define STEPPER_AZ_BOOST_PIN 15
#define STEPPER_AZ_FAULT_PIN 14

#define ENCODER_AZ_NCS_PIN 13

void setup()
{
  
  SPI.begin();
  SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));
  
  HWSerial.begin(SERIAL_BAUDRATE);
  
  HWSerial.println("hello");
  // init az
  
  pinMode(STEPPER_AZ_ENABLE_PIN, OUTPUT);
  pinMode(STEPPER_AZ_DIR_PIN, OUTPUT);
  pinMode(STEPPER_AZ_STEP_PIN, OUTPUT);
  pinMode(STEPPER_AZ_BOOST_PIN, OUTPUT);
  pinMode(STEPPER_AZ_FAULT_PIN, INPUT_PULLUP);
  
  High(STEPPER_AZ_ENABLE_PIN);
  High(STEPPER_AZ_DIR_PIN); // DIR pin HIGH turns clockwise when looking from above
  
  pinMode(ENCODER_AZ_NCS_PIN, OUTPUT);
  High(ENCODER_AZ_NCS_PIN);

  // init alt

  pinMode(STEPPER_ALT_ENABLE_PIN, OUTPUT);
  pinMode(STEPPER_ALT_DIR_PIN, OUTPUT);
  pinMode(STEPPER_ALT_STEP_PIN, OUTPUT);
  pinMode(STEPPER_ALT_BOOST_PIN, OUTPUT);
  pinMode(STEPPER_ALT_FAULT_PIN, INPUT_PULLUP);

  High(STEPPER_ALT_ENABLE_PIN);
  High(STEPPER_ALT_DIR_PIN); // DIR pin HIGH lower the dish

  pinMode(ENCODER_ALT_NCS_PIN, OUTPUT);
  High(ENCODER_ALT_NCS_PIN);




  // HWSerial.println("begin turn forward az");

  // for (int i = 0; i < 200*25600; i++)
  // {
  //     step_forward_az();
  // }

  // HWSerial.println("finished turn forward az");

  // HWSerial.println("begin quarter turn forward alt");

  // for (int i = 0; i < 140*12800/4; i++)
  // {
  //     step_forward_alt();
  // }

  // HWSerial.println("finished quarter turn forward alt");

  //flush serial
  while (HWSerial.available() > 0) {
    HWSerial.read();
  }

}

int i = 0;

void loop()
{
  HWSerial.println("<az degrees to move> <elev degrees to move>");
  HWSerial.println("example");
  HWSerial.println("45.0 -30.0");

  float angle_az = 0.0;
  float angle_elev = 0.0;

  while (HWSerial.available() <= 0) {
    delay(50);
  }
 

  angle_az = HWSerial.parseFloat();
  angle_elev = HWSerial.parseFloat();
  HWSerial.println(angle_az);
  HWSerial.println(angle_elev);

  //flush serial
  while (HWSerial.available() > 0) {
    HWSerial.read();
  }

  HWSerial.println("Start moving");
  encoders_print();

    int step_az_count = 200.0 * 12800.0 * abs(angle_az) / 360.0;
    int step_elev_count = 140.0 * 25600.0 * abs(angle_elev) / 360.0;

    int max_step_count = max (step_az_count, step_elev_count);
    int max_step_duration = max (STEP_DURATION_AZ_MS, STEP_DURATION_ALT_MS);
    
    if (angle_az > 0.0) {
      High(STEPPER_AZ_DIR_PIN);

    } else {
      Low(STEPPER_AZ_DIR_PIN);
    }
    if (angle_elev > 0.0) {
      High(STEPPER_ALT_DIR_PIN);

    } else {
      Low(STEPPER_ALT_DIR_PIN);
    }

    
    for (int j = 0; j < max_step_count; j++) {

      if(step_az_count > 0){
        High(STEPPER_AZ_STEP_PIN);
        step_az_count--;
      }
      if(step_elev_count > 0){
        High(STEPPER_ALT_STEP_PIN);
        step_elev_count--;
      }
      delayMicroseconds(max_step_duration / 2);
      Low(STEPPER_AZ_STEP_PIN);
      Low(STEPPER_ALT_STEP_PIN);
      delayMicroseconds(max_step_duration / 2);
    }
    
  

  HWSerial.println("Finished moving");
  encoders_print();
  
  HWSerial.println("\n");

  


  // encoders_print();
  // delay(50);

  // LED_On;
  // delay(200);
  // LED_Off
  // delay(200);

  // step_az();
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

  uint32_t first_word = 0;
  uint32_t second_word = 0;
  uint32_t third_word = 0;

  for (int i = 0; i < 1; i++) {
    first_word = SPI.transfer16(ZERO);
    second_word = SPI.transfer16(ZERO);
    third_word = SPI.transfer16(ZERO);
    delay(50);
  }

  High(ENCODER_AZ_NCS_PIN);

  uint32_t pos_dec = (second_word << 4) + (third_word >> 12);
  float pos_deg = (pos_dec * 360.0) / ENCODERS_MAX;

  HWSerial.print("az encoder deg ");
  HWSerial.println(pos_deg);
  HWSerial.print("az encoder dec ");
  HWSerial.println(pos_dec);
  HWSerial.print("az encoder turn counter (first word) ");
  HWSerial.println(first_word);

  HWSerial.println();

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

      HWSerial.print("alt encoder dec ");
      HWSerial.println(pos_dec);

      HWSerial.println();

  HWSerial.println("------------------------------------------");
}

void step_az()
{
  High(STEPPER_AZ_STEP_PIN);
  delayMicroseconds(STEP_DURATION_AZ_MS / 2);
  Low(STEPPER_AZ_STEP_PIN);
  delayMicroseconds(STEP_DURATION_AZ_MS / 2);
}

void step_alt()
{
  High(STEPPER_ALT_STEP_PIN);
  delayMicroseconds(STEP_DURATION_ALT_MS / 2);
  Low(STEPPER_ALT_STEP_PIN);
  delayMicroseconds(STEP_DURATION_ALT_MS / 2);
}
