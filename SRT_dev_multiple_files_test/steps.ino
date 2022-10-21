void StepOn_Az(){
    if(AzSteps){ 
        AzSTEPon; 
        AzSteps--;

        if(AzDirectionToGo) counter_test_2 += 1;
        else counter_test_2 -= 1;
    }
    LEDon;
    Timer_StepsOff_Az.trigger(STEP_SPEED_AZ / 2);
}

void StepOff_Az(){
    AzSTEPoff;
    LEDoff;
}

void StepOn_Alt(){
    if(AltSteps){ AltSTEPon; AltSteps--;}
    Timer_StepsOff_Alt.trigger(STEP_SPEED_ALT / 2);
}

void StepOff_Alt(){
    AltSTEPoff;
}

void gohome(){
    AltRef = ZENITH;
    while (AzEncMultiTurn)
    {
        if (AzCurrentDirection)
        {
            AzDIRon;
            AzRef = max_encoders - 1;
            update_steps();
        } else
        {
            AzDIRoff;
            AzRef = max_encoders - 1;
            update_steps();
        }
    }

    do
    {
        AzRef = HOME_AZ;
        update_steps();
    } while (AzDiff > HYSTERISIS);
}
