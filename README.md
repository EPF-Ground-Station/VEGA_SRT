# Small Radio Telescope

This Project consists of developing and controlling a Small Radio Telescope (SRT) to support potential research in the field of radio-astronomy. 
The code provided generates a general user interface in which one can select a satelite of choice. Once connected, the radiotelescope will move to the 
chosen satelite. 

## GS_embedded_teensy_2
Actually run on an ESP32 and not a teensy.

### Initialization ! IMPORTANT !
To enforce the security to avoid ripping the cables the code makes some assumption and the following rules should be followed :

- The APM should always be started with the cables completely untangled
- If "Error initializing turn count in constructor" is printed on start up there was a problem setting the value of the turn counter and the security likely won't work, the APM should be powered off-on (or the MCU reset maybe) until this msg does not appears (if this does not solve the problem well fuck)

### Support 4 commands :

- "point_to <degrees azimuth> <degrees elevation>"
  - azimuth grow to the east when pointed to the north
  - elevation, horizon is 0°, zenith is 90° 
  - the mechanism can't go to 90° there is a safety margin
  - for elevation input < 0° and > (90° - margin) are clamped
  - zenith safety margin is defined by ELEV_ZENITH_SAFETY_MARGIN_DEG in define.h
  - if repeated point_to cmds were to rotate the azimuth more than (360° + 350°) in one direction or another it will do a turn in the oposite direction to untangle the cables
  - if garbage is inputed instead of a floating point number I think it defaults to 0° but not sure.

- "set_north_offset <offset>"
    - offset is an encoder value, it must be between 0 and 2^20-1 (included), if not there is an error msg and the current offset is not modified
    - by default it is 0 (the microcontroller forget it when is it powered off)
    - if garbage is inputed instead of a floating point number I think it defaults to 0° but not sure.

- "untangle "
  - the space after the cmd name is important else the cmd won't be recognized
  - rotate the azimuth to the north and untangle the cables

- "stand_by "
  - the space after the cmd name is important else the cmd won't be recognized
  - put the APM in stand_by mode
  - stand_by mode disable the steppers but periodically check that azimuth stays between ±(360° + 350°) if not it execute the "untangle " cmd
  - it also set the elevation to (90°- safety_margin) and periodically check that the elevation is not lower STANDBY_ZENITH_THRESHOLD_CORRECTION_DEG (configurable in define.h) if it is lower it (re)set it to (90°- safety_margin)
  - stand_by mode is interrupted by point_to and untangle cmds

- any other input should return "Unrecognized command name"

### Errors
point_to and untangle give a feedback telling if there was an error during the execution of the commands (cannot get a valid value from an encoder). The stand_by mode does it too but does not print smth when there was no errors (to avoid spamming as it is executed periodically).

### Code quality and structure
The code could use some refactoring to delete duplicated parts and also remove all the commented out "//HWSerial.println("DEBUG..."
The current version flashed on the ESP still has all the debug prints uncommented, feel free to reflash it with the last version.

For simplicity and because we are using arduino all classes are implemented in header files

- GS_embedded_teensy_2.ino : command handling
- define.h : all configurable constants
- AntennaPointingMechanism.h : control logic
- EncoderBase.h : virtual base class with common function(s) for single and multi turn encoders
- Encoder.h and EncoderMultiTurn.h : classes inherinting from EncoderBase respectivelly represening single and multi turn encoder
- Stepper.h : class representing a stepper, used a bit like a struct as all of the control is done in AntennaPointingMechanism
- Error.h : define a simple struct to report errors

### More documentation
See <documentation.md>


# ------- old stuff that was in the README -----------

## Files : 
1) main.py <br>
    Contains the class SRTApp and the main loop. Calling on an instance of the class SRTApp generates a GUI with which a satelite can be chosen for the telescope to follow.
2) satelite.py <br>
    Contains the code that extracts and preprocesses the list of active satelites and their corresponig TLEs


## Packages : 
In order to get the programm up and running some packages need to get installed: 

1) **pyserial**<br>
   this can be easily done by running the command: conda install -c anaconda pyserial



## Handeling : 


## Contributors : 

