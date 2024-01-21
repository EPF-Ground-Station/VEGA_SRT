# Very Elegant Galactic Antenna (VEGA)

Welcome to the VEGA radio-telescope repository! This project consists in developing and controlling a Small Radio Telescope (SRT) to support potential research in the field of radio-astronomy. 

The radio-telescope, nominal since summer 2023, is currently operated by the Callista association, the EPFL astronomy club.

The device itself is installed on the roof of EPFL EL-B building. The control room currently in service is located in EL-B 216, where a central computer was deployed thanks to the support of the Physics Department.

Although all experimental operations ought to be conducted in EL-B 216 for safety concerns, VEGA is remotely operable via the EPFL network and VPN, allowing EPFL users to connect themselves to the antenna backend from any place in the world!

All the code documentation is generated from docstrings by Sphinx and is hosted at : https://vega-srt.readthedocs.io

### Installation
For now, no sophisticated installation procedure was defined, so that it is enough for deploying the interface to the radiotelescope to either clone this repository locally and run the GUI client, or connect via VNC to VEGA's computer and run operations from there, in either script/command line or GUI interface.

However, some packages are required for the client to work properly, namely PySide6 and its Qt library dependencies. To install PySide6, refer to its documentation : https://pypi.org/project/PySide6/


## Table of Contents
1. The client/server interface
2. Operating in command line
3. Scripting VEGA



