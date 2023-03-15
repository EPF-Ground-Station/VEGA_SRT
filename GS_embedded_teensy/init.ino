void init_pins (){
  pinMode(AzENABLEPin,OUTPUT);
  pinMode(AltENABLEPin,OUTPUT);
  pinMode(AltDIRPin,OUTPUT);
  pinMode(AltSTEPPin,OUTPUT);
  pinMode(AltBOOSTPin,OUTPUT);
  pinMode(AltFAULTPin,INPUT_PULLUP);
  pinMode(AzDIRPin,OUTPUT);
  pinMode(AzSTEPPin,OUTPUT);
  pinMode(AzBOOSTPin,OUTPUT);
  pinMode(AzFAULTPin,INPUT_PULLUP);
  pinMode(AzSCKPin,OUTPUT);
  pinMode(AzNCSPin,OUTPUT);
  pinMode(AzMISOPin,INPUT);
  //pinMode(AzMOSIPin,OUTPUT);
  pinMode(AltSCKPin,OUTPUT);
  pinMode(AltNCSPin,OUTPUT);
  pinMode(AltMISOPin,INPUT_PULLUP);
  pinMode(AltMOSIPin,OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);
}

void init_encoders_rel(){
    AzNCSoff;
    delayMicroseconds(5);

    for (int i = 15; i >= 0; i--)
    {
        AzSCKon;
        delayNanoseconds(250);
        if (AzMISOisHIGH) AzEncMultiTurnInit |= (1<<i);
        AzSCKoff;
        delayNanoseconds(250);
    }

    AltNCSoff;
    delayMicroseconds(5);

    for (int i = 19; i >= 0; i--)
    {
        AzSCKon;
        AltSCKon;
        delayNanoseconds(250);
        if (AzMISOisHIGH) AzEncPosInit |= (1<<i);
        if (AltMISOisHIGH) AltEncPosInit |= (1<<i);
        AzSCKoff;
        AltSCKoff;
        delayNanoseconds(250);
    }

    AzSCKon;
    AltSCKon;
    delayNanoseconds(250);
    AzSCKoff;
    AltSCKoff;
    delayNanoseconds(250);
    AzSCKon;
    AltSCKon;
    delayNanoseconds(250);
    AzSCKoff;
    AltSCKoff;
    delayNanoseconds(250);

    AzSCKon;
    AltSCKon;
    delayNanoseconds(250);
    AzEncError = !AzMISOisHIGH;
    AltEncError = !AltMISOisHIGH;
    AzSCKoff;
    AltSCKoff;
    delayNanoseconds(250);

    AzSCKon;
    AltSCKon;
    delayNanoseconds(250);
    AzEncWarning = !AzMISOisHIGH;
    AltEncWarning = !AltMISOisHIGH;
    AzSCKoff;
    AltSCKoff;
    delayNanoseconds(250);

    AzNCSon;
    AltNCSon;
}

void init_encoders_abs(){
    AzEncMultiTurnInit = 35;
    AzEncPosInit = 484399;
    AltEncPosInit = 275923;
}
