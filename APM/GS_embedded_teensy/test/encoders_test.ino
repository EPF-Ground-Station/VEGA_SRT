void Encoders() {
    AltEncPosAbs = 0, AzEncPosAbs = 0;
    AzEncMultiTurnAbs = 0;
    AltEncCRC = 0, AzEncCRC = 0;

    AzNCSoff;
    delayMicroseconds(5);

    for (int i = 15; i >= 0; i--)
    {
        AzSCKon;
        delayNanoseconds(250);
        if (AzMISOisHIGH) AzEncMultiTurnAbs |= (1<<i);
        AzSCKoff;
        delayNanoseconds(250);
    }

    if (AzEncMultiTurnAbs > AzEncMultiTurnInit) {
        AzEncMultiTurn = AzEncMultiTurnAbs - AzEncMultiTurnInit;
        AzCurrentDirection = 1;
    }
    else {
        AzEncMultiTurn = AzEncMultiTurnInit - AzEncMultiTurnAbs;
        AzCurrentDirection = 0;
    }

    AltNCSoff;
    delayMicroseconds(5);

    for (int i = 19; i >= 0; i--)
    {
        AzSCKon;
        AltSCKon;
        delayNanoseconds(250);
        if (AzMISOisHIGH) AzEncPosAbs |= (1<<i);
        if (AltMISOisHIGH) AltEncPosAbs |= (1<<i);
        AzSCKoff;
        AltSCKoff;
        delayNanoseconds(250);
    }

    if (AzEncPosAbs > AzEncPosInit) {
        AzEncPos = AzEncPosAbs - AzEncPosInit;
        if (!AzEncMultiTurn) AzCurrentDirection = 1;
    }
    else {
        AzEncPos = AzEncPosAbs + max_encoders;
        AzEncPos -= AzEncPosInit;
        if (!AzEncMultiTurn) AzCurrentDirection = 0;
    }

    if (AltEncPosAbs > AltEncPosInit) {
        AltEncPos = AltEncPosAbs - AltEncPosInit;
        AltCurrentDirection = 1;
    }
    else {
        AltEncPos = AltEncPosAbs + max_encoders;
        AltEncPos -= AltEncPosInit;
        AltCurrentDirection = 0;
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

//    print_encoders();
    print_test2();
}
