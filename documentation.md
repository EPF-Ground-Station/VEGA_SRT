# Documentation

## Encoders
    green   MISO
    gray    GND
    brown   VCC
    red     SCK
    yellow  GND
    white   GND
    pink    not connected
    black   not connected
    purple  not connected
    blue    N_CS

Encoders documentation <https://www.rls.si/eng/fileuploader/download/download/?d=1&file=custom%2Fupload%2FMBD01_10EN_datasheet_bookmark.pdf>
(<https://www.rls.si/eng/media-center?search=MBD01> if the link above doesn't work)

## UART to USB converter
    purple  GND
    green   TX
    red     RX
    
## Steppers
	red     STEP
	yellow  DIR
    	black   ENABLE
	gray    GND
  
## Other infos on drivers, steppers and encoders
- Right driver in the box controls elevation
- Left driver in the box controls azimuth

- Min az driver step interval tested = 20us
- Min elev driver step interval tested = 30us (20us is too low)

- Az has a 200 reduction
- Elev has a 140 reduction

- Az driver is configured at 12800 microsteps / rev
- Elev driver is configured at 25600 microsteps / rev
  
- Elev stepper with DIR pin HIGH lower the dish
- Az stepper with DIR pin HIGH turns clockwise when looking from above
  
- Elev encoder : lowering decrease its value
- Az encoder : turning clockwise (looking from above) increase its value
  
- for encoders use GPIO instead of builtin SPI CS (doesn't work for some reason else)
 
## MCU
A NodeMCU ESP-WROOM-32 Development Board is used
(https://www.elektronik-kaufen.ch/products/nodemcu32?variant=41643637047472)

- Don't use GPIO0 as it create a permanent reset or something

### To program the esp32
- if it doesn't work try disconnecting rx and tx of the hardware serial cable (The UART to USB converter connect them in a way that prevent programming sometime ??)

- Press the boot button while programming (else it will complain it's not in boot mode)
