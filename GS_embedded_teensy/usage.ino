void sat_tracker(){
    if (check_cable_entanglement()){
        gohome();
    }
    else {
        update_reference_sat();
        update_steps();
    }
}

void test1(){
    AltRef = AltPointsCoordinates[point_counter];
    AzRef = AzPointsCoordinates[point_counter];

    if (point_counter >= (sizeof(AltPointsCoordinates) / sizeof(*AltPointsCoordinates))){
        delay(1000);
        point_counter = 0;
    }  
    
   update_steps();
}

void test2(){
    AltRef = AltPointsCoordinates[point_counter];
    AzRef = AzPointsCoordinates[point_counter];

    if (point_counter == 0) counter_test_2 = 0;

    if (point_counter >= 2){
        delay(1000);
        point_counter = 0;
    }  
    
   update_steps();
}
