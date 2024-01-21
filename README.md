# Very Elegant Galactic Antenna (VEGA)

Welcome to the VEGA radio-telescope repository! This project consists in developing and controlling a Small Radio Telescope (SRT) to support potential research in the field of radio-astronomy. 

The radio-telescope, nominal since summer 2023, is currently operated by Callista, the EPFL astronomy club.

The device itself is installed on the roof of EPFL EL-B building. The current control room is located in EL-B 216, where a central computer was deployed thanks to the support of the Physics Department.

Although all experimental operations ought to be conducted in EL-B 216 for safety concerns, VEGA is remotely operable via the EPFL network and VPN, allowing EPFL users to connect themselves to the antenna backend from any place in the world!

All the code documentation is generated from docstrings by Sphinx and is hosted at : https://vega-srt.readthedocs.io

### Installation
For now, no sophisticated installation procedure has been defined yet, so that it is enough for using VEGA to either clone this repository locally and run the GUI client, or connect via VNC to VEGA's computer and run operations from there, in either script/command line or GUI interface mode.

However, some packages are required for the client to work properly, namely PySide6 and its Qt library dependencies. To install PySide6, refer to its documentation : https://pypi.org/project/PySide6/


## Table of Contents
1. Global Architecture
2. The client/server interface
3. Operating in command line
4. Scripting VEGA


## Global Architecture

The VEGA radiotelescope is motorized and its motion is monitored by an Antenna Pointing Mechanism (APM), the code of which is available in the APM folder, and runs on an ESP32 in VEGA's electrical cabinet. Slewing commands are sent from VEGA's computer to the APM via an UART serial port. 

To operate this APM, several interface modes can be chosen : either using lib_SRT in command line (see section 3) by logging in VEGA's PC via VNC, or using the provided graphical interface client (see section 2), given mainserver.py is running on VEGA's PC. Notice the critical importance to avoid multiple connexions to VEGA, and as such the interface development is still in progress to allow supervision of the server utilization. 

One of the main constraint/driver of the lib_SRT architecture is the synchronous mode of VEGA's encoder which forbids multiple simultaneous commands to be executed by the APM. Therefore, everything was made to avoid sending multiple commands to the APM via e.g. different python threads. This reflexion led to the choice of Qt Signals and Slots framework, which turned appropriate for our purpose.

## Client/Server

Hereafter is explained how to get the best out of VEGA using its graphical interface.

### The Server

The mainserver.py script is only meant to run on VEGA's computer, and as such all initialization parameter such as the address of the serial port on which to communicate with the Antenna Pointing Mechanism are filled accordingly. The server takes care of the first handshake with incoming TCP connexions from clients, upon which it decides wether or not to accept the connexion. In particular, only one client connexion at a time is allowed.




