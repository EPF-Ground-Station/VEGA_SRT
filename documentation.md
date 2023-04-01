encoders :
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

UART to USB converter
    (long black cable)
    purple  GND
    green   TX
    red     RX
    
  
  right driver is alt
  left driver is az
  
  stepper pins
  ============
	  red STEP
	  yellow DIR
	  black ENABLE
	  gray	GND ?
	  
min az driver step interval tested = 20us
min alt driver step interval tested = 30us (20us too low)

  az 12800 microstep / rev and 200 reduction
  alt 25600 microstep / rev and 140 reduction
  
  alt with pin dir high gets down
  az with pin dir high turn clockwise when looking from above
  
  encoder alt lowering decreasing
  encoder az  turn clockwise (looking from above) increase
  
 for encoders use GPIO instead of builtin SPI CS (doesn't work for some reason else)
 
 to program the esp32 (model https://www.elektronik-kaufen.ch/products/nodemcu32?variant=41643637047472&currency=CHF)
 	disconnect rx and tx of hardware serial cable
 	press boot mode button while programming
 	
 don't use the GPIO0 as it create a permanent power on reset
