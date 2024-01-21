## Antenna Pointing Mechanism 

In this folder are stored the Arduino code of the VEGA Radiotelescope ESP-32, and the archives from the team who first deployed the antenna on the roof of EPFL EL-B building.

# Contents :

- GS_embedded_teensy and GS_embedded_teensy2
- documentation.md
- PCB_SRT
- Various tests

# GS_embedded_teensy(2) :

In these two folders are stored the code to be uploaded on the ESP32 (actually not a teensy) of VEGA's electrical cabinet upon each modification. The GS_embedded_teensy_2/GS_embedded_teensy_2.ino runs the Antenna Pointing Mechanism loop. In this file the processing of commands sent by UART serial port from the electrical cabinet computer can be found and modified. 

# documentation.md :

In this file Raphaël Temperli (EPFL Spacecraft Team's Guru of Software) documented the functioning of encoders, along with some procedures and troubleshooting to correctly upload the Arduino code on the ESP32 upon modification.

# PCB_SRT :

Folder containing funny drawings printed on the PCB of the ESP32 (there are the 2D and 3D files of the pcb, too)

# Various tests :

Tests files, the goal of which is still to be determined. Used by the initial team at the manufacturing stage of VEGA.