void print_encoders(){
    Serial.print("Az Multiturn : ");
    Serial.println(AzEncMultiTurn);

    Serial.print("Az Position : ");
    Serial.println(AzEncPos * 360 / max_encoders);
    Serial.print("Az Direction : ");
    Serial.println(AzCurrentDirection);
    Serial.println("");

    Serial.print("Alt Position : ");
    Serial.println(AltEncPos * 360 / max_encoders);
    Serial.print("Alt Direction : ");
    Serial.println(AltCurrentDirection);
    Serial.println("");

    Serial.print("Az Error : ");
    Serial.println(AzEncError);
    Serial.print("Alt Error : ");
    Serial.println(AltEncError);

    Serial.print("Az Warning : ");
    Serial.println(AzEncWarning);
    Serial.print("Alt Warning : ");
    Serial.println(AltEncWarning);

    Serial.println("-------------------------------");
}

void print_test2(){
    Serial.print(counter_test_2);
    Serial.print(" ");
    Serial.println(AzEncPos);
}
