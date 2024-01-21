void print_encoders(){
    HWSerial.print("Az Multiturn : ");
    HWSerial.println(AzEncMultiTurn);

    HWSerial.print("Az Position : ");
    HWSerial.println(AzEncPos * 360 / ENCODERS_MAX);
    HWSerial.print("Az Direction : ");
    HWSerial.println(AzCurrentDirection);
    HWSerial.println("");

    HWSerial.print("Alt Position : ");
    HWSerial.println(AltEncPos * 360 / ENCODERS_MAX);
    HWSerial.print("Alt Direction : ");
    HWSerial.println(AltCurrentDirection);
    HWSerial.println("");

    HWSerial.print("Az Error : ");
    HWSerial.println(AzEncError);
    HWSerial.print("Alt Error : ");
    HWSerial.println(AltEncError);

    HWSerial.print("Az Warning : ");
    HWSerial.println(AzEncWarning);
    HWSerial.print("Alt Warning : ");
    HWSerial.println(AltEncWarning);

    HWSerial.println("-------------------------------");
}

void print_test2(){
    HWSerial.print(counter_test_2);
    HWSerial.print(" ");
    HWSerial.println(AzEncPos);
}
