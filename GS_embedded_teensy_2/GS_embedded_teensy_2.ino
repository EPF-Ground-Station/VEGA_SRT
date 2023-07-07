#include "define.h"

#include "AntennaPointingMechanism.h"
#include "Error.h"

AntennaPointingMechanism *apm = nullptr;

float az, elev = 0.0;

void print_status(ErrorStatus status);

void setup() {
    
    HWSerial.begin(SERIAL_BAUDRATE);

    HWSerial.println("HELLO DEBUG");

    // constructor cannot be called before setup because it uses pins
    apm = new AntennaPointingMechanism();

    HWSerial.println("HELLO DEBUG 2");


    //LED_On;
    //antenna->empty_water();
    //LED_Off;

    //flush serial
    while (HWSerial.available() > 0){
        HWSerial.read();
    }

}

void loop() {

    // az and elev are in degree
    // az grow to the east (aimed at the north)
    // elev is 0° at the horizon and grow toward zenith
    if (HWSerial.available() > 0){

        String cmd_name = HWSerial.readStringUntil(' ');
        
        //TODO how detect invalid parameters when parse function time out
        

            if(cmd_name.equals("point_to"))
            {
                az = HWSerial.parseFloat();
                elev = HWSerial.parseFloat();
                HWSerial.println("Got az : " + String(az) + " elev : " + String(elev));
                ErrorStatus status;
                status = apm->point_to(az, elev);
                print_status(status);
                HWSerial.println("Finished pointing");
            }

            else if(cmd_name.equals("set_north_offset"))
            {
                int offset;
                offset = HWSerial.parseInt();
                HWSerial.println("Got " + String(offset));
                if(offset >= 0 && offset <= ENCODERS_MAX){
                    apm->setNorthOffset(offset);
                    HWSerial.println("Set north offset");
                }else{
                    HWSerial.println("Error offset should be positive and not greated than " + String(ENCODERS_MAX));
                }
            }
            if(cmd_name.equals("stand_by"))
            {
                apm->standbyEnable();
                HWSerial.println("Standby enabled");
            }

            if(cmd_name.equals("untangle"))
            {
                HWSerial.println("Untangling...");
                apm->untangle_north();
                HWSerial.println("Untangled");
            }
            else
            {
                HWSerial.println("Unrecognized command name");
            }
        

        //flush serial
        while (HWSerial.available() > 0){
            HWSerial.read();
        }

    }

    ErrorStatus status = apm->standByUpdate();
    print_status(status);

    delay(50);
}

void print_status(ErrorStatus status){
    switch (status.type) {
                    case ErrorType::ERROR:
                        HWSerial.println("error");
                        break;
                    case ErrorType::WARNING:
                        HWSerial.println("warning");
                        break;
                    case ErrorType::NONE:
                        HWSerial.println("none");
                        break;
                }

                HWSerial.println(status.msg.c_str());
}