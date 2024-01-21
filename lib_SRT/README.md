# The SRT library

This library is aimed at defining all classes and parameters relevant to the operation of VEGA radiotelescope.

The constants in beginning of the file are fine-tuned for our antenna's location, storage system etc.

The main class of the package is the SRT, which owns a SerialPort object and is thus thought as the only class being
able to communicate with the Antenna Pointing Mechanism (APM) at a time. For more about the APM, see the embedded_teensy
documentation.

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

@LL