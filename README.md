# Very Elegant Galactic Antenna (VEGA)

Welcome to the VEGA radio-telescope software repository! This project consists in developing and controlling a Small Radio Telescope (SRT) to support potential research in the field of radio-astronomy. 

The radio-telescope, nominal since summer 2023, is currently operated by Callista, the EPFL astronomy club.

The device itself is installed on the roof of EPFL EL-B building. The current control room is located in EL-B 216, where a central computer was deployed thanks to the support of the Physics Department.

Although all experimental operations ought to be conducted in EL-B 216 for safety concerns, VEGA is remotely operable via the EPFL network and VPN, allowing EPFL users to connect themselves to the antenna backend from any place in the world!

All the code documentation is generated from docstrings by Sphinx and is hosted at : https://vega-srt.readthedocs.io

### Installation
For now, no sophisticated installation procedure has been defined yet, so that it is enough for using VEGA to either clone this repository locally and run the GUI client, or connect via VNC to VEGA's computer and run operations from there, in either script/command line or GUI interface mode.

However, some packages are required for the client to work properly, namely PySide6 and its Qt library dependencies. To install PySide6, refer to its documentation : https://pypi.org/project/PySide6/

Another option for the distribution of the client is to use Nuitka. A standalone executable of mainclient.py can be generated e.g. in EL-B 216 by using the Anaconda Prompt command :
```python -m nuitka --standalone --enable-plugin=pyside6 mainclient.py ```
Optionally one can use the additional ```--disable-console``` option in order to get rid of the console popping up at launch of the executable. However this console might ne handy for debugging / troubleshooting.


## Table of Contents
1. Global Architecture
2. The client/server interface
3. Operating in command line
4. Scripting VEGA


## Global Architecture

### Hardware

The VEGA radiotelescope is motorized and its motion is monitored by an Antenna Pointing Mechanism (APM), the code of which is available in the APM folder, and runs on an ESP32 in VEGA's electrical cabinet. Slewing commands are sent from VEGA's computer to the APM via an UART serial port. Measurements are performed via the HackRF Software Defined Radio (SDR) connected to VEGA's computer and antenna acquisition pipeline.

### Interface 

To operate this APM, several interface modes can be chosen : either using lib_SRT in command line (see section 3) by logging in VEGA's PC via VNC, or using the provided graphical interface client (see section 2), given mainserver.py is running on VEGA's PC. Notice the critical importance to avoid multiple connexions to VEGA, and as such the interface development is still in progress to allow supervision of the server utilization. 

### Dependencies

One of the main constraint/driver of the lib_SRT architecture is the synchronous mode of VEGA's encoder which forbids multiple simultaneous commands to be executed by the APM. Therefore, everything was made to avoid sending multiple commands to the APM via e.g. different python threads. This reflexion led to the choice of Qt Signals and Slots framework, which turned appropriate for our purpose.

### Data storage

In order to store high amounts of radioastronomic data, the Physics department graciously provided some storage on their NAS. The path can be updated anytime under lib_SRT/define.py .


## Client/Server

Hereafter is explained how to get the best out of VEGA using its graphical interface.

### The Server

The mainserver.py script is only meant to run on VEGA's computer, and as such all initialization parameter such as the address of the serial port on which to communicate with the Antenna Pointing Mechanism are filled accordingly. The server takes care of the first handshake with incoming TCP connexions from clients, upon which it decides wether or not to accept the connexion. In particular, only one client connexion at a time is allowed.

For more about the server, check the code and the online documentation.

### The client

The mainclient.py script can be run from any computer and pops up a launcher from which connexion to the server can be established. For now, the connexion is only feasible if the user's computer is connected to the EPFL network, either physically, on EPFL wi-fi or via the VPN. 

Once connexion is established, the main client window pops up, allowing to perform slew, tracking, data acquisition and basic plotting. 

For more about the client, check the code and the online documentation.

## Command Line mode

VEGA can also be used in command line, provided the server is not running in order to avoid multiple access to the APM from several users. Note this mode can only be used by accessing VEGA's computer via VNC.

Under Scripts, the python interpreter can be opened by typing "python3" in the command line. From there, run "from SRT_inline import *". That's all! You can now operate VEGA by typing python command from lib_SRT off the fly.

## Scripting VEGA

Another utilization of SRT_inline is to import it in a script. Under Scripts, examples of such automated observations can be found. This feature allows to completely plan a measurement campaign with customized features. Future envisioned projects could for instance include a complete, automated of the Milky Way H21 radiations.
