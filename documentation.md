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
	  
min STEP interval tested = 100ms
  
  
  alt with pin dir high gets down
  az with pin dir high turn clockwise when looking from above
  
 for encoders use GPIO instead of builtin SPI CS (doesn't work for some reason else)
