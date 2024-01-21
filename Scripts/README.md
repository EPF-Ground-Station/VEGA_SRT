# Scripting VEGA

In this folder is included SRT_inline.py, a shortcut for instantiating correctly the Srt class for planned measurements and operations.

## Scripting Procedure

At beginning of your script, include the line :

```from SRT_inline import *```

From now on, the SRT object is instantiated and all method of the Srt class can be used casually. Find them at https://vega-srt.readthedocs.io/en/latest/lib_SRT.html#lib_SRT.Srt.Srt .

Notice the multithread approach needs to be taken into account when measuring within a script. For instance the method SRT.waitObs must be used between the beginning of an observation and the next slewing motion.

Refer to testVirgo.py for an example.

## Command line on the fly

the SRT_inline module can also be imported in a python interpreter to directly operate VEGA by entering python commands on the fly. Simply feed the interpreter with commands such as :
```SRT.pointAzAlt(30,30)```

to command VEGA to slew to coordinates Az = 30°, Alt = 30°.
