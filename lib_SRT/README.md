# The SRT library

This library is aimed at defining all classes and parameters relevant to the operation of VEGA radiotelescope.

## Definitions

The constants in define.py are fine-tuned for our antenna's location, storage system etc. Here you can modify tracking 
rates, ping rates, North calibration constant etc. Those should not be changed without serious study of the consequences
on the global functioning of the system. For example, changing the ping rate to higher may cause the APM to go to standby
mode in the middle of an observation for inactivity. Check APM package for more.

## SRT

The main class of the package is the SRT, which owns a SerialPort object and is thus thought as the only class being
able to communicate with the Antenna Pointing Mechanism (APM) at a time. For more about the APM, see the embedded_teensy
documentation.

## Others : SerialPort and QThreads

Other classes are the private class SerialPort which monitors communication with APM via the serial module, and
QThreads such as QPing and QTracker, all owned and instantiated by the SRT class, which monitor background tasks of the
APM.

The main constraint of our current design is the fact the encoders of the mount work in synchronous mode, i.e. they can
only execute one task at a time. In particular, a task cannot be stopped by software. This implies only one command
should be sent to the APM at a time by the user interface.

This strong requirement led to use the Qt library in the implementation of the multi-thread interface. QThreads
communicate with one another via QSignals which can carry variables such as strings. This way, all background tasks
that require to send commands to the APM rely on the SRT instance to actually send the corresponding messages via the
serial port, by emitting QSignals carrying their messages, which are connected to appropriate slots in the SRT class.

For more about this multi-threading architecture, see the SRT class.

### Troubleshooting with QThreads

A recurrent ``Multiple access on port`` error occured when trying to implement the water evacuation routine. The teaching 
of this seems to be that long methods, containing several commands to the APM overlap with commands sent by signal catching.

The problem was an overlapping between the Pings (sent after sendPing signal is caught) and the several pointing commands
of ``evacuate_water``. My hypothesis is even though in general slots only execute one after another, here the ``evacuate_water``
is considered as plain function and as such, if the Ping signal is received between two pointing commands, the ``onPingSignal`` slot 
is triggered simultaneously with the execution of the following line of the method, i.e. another command sent to APM. This
seems to cause the overlap. The hypothesis seems to be corroborated by the fact this trouble does not occur when operating 
normally the APM with commands such as ``pointAzAlt``, which only execute one command to the APM. 

The problem was solved by only activating the Ping after the evacuation routine. If the problem occurs again, the entire 
QThread structure should probably be revised to deliver a more robust one (ish).

If this hypothesis turns true, then : 
- Coding new methods of class SRT with more than one APM command should be avoided
- If necessary, these commands can be implemented externally to the SRT class in functions OR
- Those commands may eventually be implemented directly in the APM arduino, then as a single-APM command SRT method


## Virgo

For now, the data acquisition is performed using the external virgo package. Slight modifications were brought to the 
original version, which explains why it is stored as a local subpackage. In the long run, it might be interesting to 
modify further in order to gain more control on the data processing pipeline, especially within an academic framework.
