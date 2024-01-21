char sat_name[25];

#define HWSerial Serial

void setup() {

  HWSerial.begin(115200);

  delay(5000);

  HWSerial.println("testst");

  while (HWSerial.available() <= 0){}
  while (HWSerial.available() > 0){
     /*
        for(int i = 0; i < 5; i++){
            sat_name[i] = (char) HWSerial.read();
        }
       */
        HWSerial.print( (char) HWSerial.read());
        
      
  }
  delay(200);
  HWSerial.println("sat_name");

}
int i = 0;
void loop() {
  // put your main code here, to run repeatedl
  //HWSerial.println(i);
  delay(50);
  i++;

}
