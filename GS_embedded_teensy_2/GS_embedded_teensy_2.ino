#include "define.h"

#include "AntennaPointingMechanism.h"
#include "Error.h"
#include <string>

AntennaPointingMechanism *apm = nullptr;

float az, elev = 0.0;
float az_current;
float alt_current;

void print_status(ErrorStatus status, bool print_success, std::string feedback = "");

void setup() {
    
    HWSerial.begin(SERIAL_BAUDRATE);

    //HWSerial.println("HELLO DEBUG");

    // constructor cannot be called before setup because it uses pins
    apm = new AntennaPointingMechanism();

    //HWSerial.println("HELLO DEBUG 2");


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
        ErrorStatus status;     // None type, empty error message
        std::string feedback("");   // Message to return
        //TODO how detect invalid parameters when parse function time out
        

            if(cmd_name.equals("point_to"))
            {
                az = HWSerial.parseFloat();
                elev = HWSerial.parseFloat();

                status = apm->point_to(az, elev);
                feedback = "Finished pointing";

            }

            else if(cmd_name.equals("set_north_offset"))
            {
                int offset;
                offset = HWSerial.parseInt();

                if(offset >= 0 && offset <= ENCODERS_MAX){
                    apm->setNorthOffset(offset);
                    feedback = "Set north offset to ";
                    feedback = feedback + std::to_string(offset);
                }else{
                    status.type = ErrorType::ERROR;
                    status.msg = ("Error offset should be positive and not greater than " + std::to_string(ENCODERS_MAX));
                    feedback = "Received value : ";
                    feedback = feedback + std::to_string(offset);
                }
            }
            else if(cmd_name.equals("stand_by"))
            {
                status = apm->point_zenith();
                apm->standbyEnable();
                feedback = ("Standby enabled");
            }

            else if(cmd_name.equals("untangle"))
            {
                status = apm->untangle_north();
                feedback = "Untangled";
            }

            else if(cmd_name.equals("getAz"))
            {
                status = apm->getCurrentAz(az_current);
                feedback = std::to_string(az_current);

            }

            else if(cmd_name.equals("getAlt"))
            {
                status = apm->getCurrentAz(alt_current);
                feedback = std::to_string(alt_current);

            }

            else
            {
                status.type = ErrorType::ERROR;
                status.msg = ("Unrecognized command name");
            }
        

        //flush serial
        while (HWSerial.available() > 0){       // To remove? Seems to forbid multiple commands. If we wait for feedback
            HWSerial.read();                    // before sending more command, we can keep it
        }
      print_status(status, true, feedback);
    }
    

    ErrorStatus status = apm->standByUpdate();
    print_status(status, false);

    delay(50);
}

void print_status(ErrorStatus status, bool print_success, std::string feedback){

    /// Format : {Type | msg} with Type in (Error, Warning, Success) and msg = Error msg (if any) + feedback

    std::string response = "";
    switch (status.type) {
                    case ErrorType::ERROR:
                        response = "Error | " + status.msg ;
                        if (feedback != "") {response += ". APM returned " + feedback;}
                        break;
                    case ErrorType::WARNING:
                        response = "Warning | " + status.msg ;
                        if (feedback != "") {response += ". APM returned " + feedback;}
                        break;
                    case ErrorType::NONE:
                        if(print_success){
                            response = "Success | " + feedback;
                        }
                        break;
                }

                if(response.length() > 0){
                    HWSerial.println(response.c_str()); // .c_str() ?
                }
                    
}