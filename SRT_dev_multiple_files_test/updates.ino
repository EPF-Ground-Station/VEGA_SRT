void update_reference_sat(){
    if(Serial.available()){
        for(int i = 0; i < 25; i++){
            sat_name[i] = (char) Serial.read();
        }
        Serial.read();

        for(int i = 0; i < 70; i++){
            TLE1[i] = (char) Serial.read();
        }
        Serial.read();

        for(int i = 0; i < 70; i++){
            TLE2[i] = (char) Serial.read();
        }
        Serial.read();

        sat.site(46.5500,6.6170, 616);
        sat.init(sat_name,TLE1,TLE2);
    }

    sat.findsat((unsigned long) now() - 7199);

    AzRef = sat.satAz * max_encoders / 360.0;
    AltRef = sat.satEl * max_encoders / 360.0;

    // Serial.println("-------------------------------");
    // Serial.print("AzRef : ");
    // Serial.println(AzRef);
    // Serial.print("AltRef : ");
    // Serial.println(AltRef);
    // Serial.println("-------------------------------");
}

void update_steps(){

    if (AltRef > AltEncPos)
    {
        AltDiff = AltRef - AltEncPos;
        AltDirectionToGo = 1;
        if (AltDiff > (524288 - 1)) AltDirectionToGo = 0;
    } else if (AltRef < AltEncPos)
    {
        AltDiff = AltEncPos - AltRef;
        AltDirectionToGo = 0;
        if (AltDiff > (524288 - 1)) AltDirectionToGo = 1;
    } else {
        AltDiff = 0;
    }

    if (AzRef > AzEncPos)
    {
        AzDiff = AzRef - AzEncPos;
        AzDirectionToGo = 1;
        if (AzDiff > (524288 - 1)) AzDirectionToGo = 0;
    } else if (AzRef < AzEncPos)
    {
        AzDiff = AzEncPos - AzRef;
        AzDirectionToGo = 0;
        if (AzDiff > (524288 - 1)) AzDirectionToGo = 1;
    } else {
        AzDiff = 0;
    }

    if (((AltEncPos < AltRef + HYSTERISIS) && (AltEncPos > AltRef - HYSTERISIS)) || ((AltRef < HYSTERISIS) && (AltEncPos > (max_encoders - HYSTERISIS + AltRef)))) AltDiff = 0;
    if (((AzEncPos < AzRef + HYSTERISIS) && (AzEncPos > AzRef - HYSTERISIS)) || ((AzRef < HYSTERISIS) && (AzEncPos > (max_encoders - HYSTERISIS + AzRef)))) AzDiff = 0;

    if (AltEncPosAbs < 180000) AltDiff = 0;
    //if ((AzEncMultiTurnAbs == 35 && AzEncPosAbs < 399485) || (AzEncMultiTurnAbs == 35 && AzEncPosAbs > 535884)) AzDiff = 0;

    if (AltDiff == 0 && AzDiff == 0) {
        delay(500);
        point_counter += 1;
    }

    if (AltDirectionToGo)
    {
        AltDIRon;
        AltSteps = AltDiff * ALT_REDUCTION * MICROSTEPS / max_encoders;
    } else
    {
        AltDIRoff;
        AltSteps = AltDiff * ALT_REDUCTION * MICROSTEPS / max_encoders;
    }

    if (AzDirectionToGo)
    {
        AzDIRon;
        AzSteps = AzDiff * MICROSTEPS / max_encoders;
    } else
    {
        AzDIRoff;
        AzSteps = AzDiff * MICROSTEPS / max_encoders;
    }
}

int check_cable_entanglement(){
    if (AzEncMultiTurn >= 2) return 1;
    else return 0;
}
