#ifndef STEPPER_H
#define STEPPER_H

#include "define.h"

class Stepper {

    public:
    enum class Direction { Forward, Backward };

    private:

    int step_pin, dir_pin, enable_pin, boost_pin, fault_pin = -1;

    int step_duration_us = 0;

    public:

    Stepper(int step_pin, int dir_pin, int enable_pin, int boost_pin, int fault_pin, int step_duration_us):
        step_pin(step_pin),
        dir_pin(dir_pin),
        enable_pin(enable_pin),
        boost_pin(boost_pin),
        fault_pin(fault_pin),
        step_duration_us(step_duration_us) {

        pinMode(step_pin, OUTPUT);
        pinMode(dir_pin, OUTPUT);
        pinMode(enable_pin, OUTPUT);
        pinMode(boost_pin, OUTPUT);
        pinMode(fault_pin, INPUT_PULLUP);

    }

    ~Stepper(){
        
    }
    
    int getStepDuration(){
        return step_duration_us;
    }

    void enable(){
        High(enable_pin);
    }

    void disable(){
        Low(enable_pin);
    }

    void stepRiseEdge(){
        High(step_pin);
    }

    void stepLowerEdge(){
        Low(step_pin);
    }

    void setDirection(Direction dir){
        if(dir == Direction::Forward){
            High(dir_pin);
        } else{
            Low(dir_pin);
        }
    }
/*
    void step(int steps){

        Direction dir = Direction::Forward;

        if(steps < 0){
            steps = -steps;
            dir = Direction::Backward;
        }

        for(int i = 0; i < steps; i++){
            if(dir == Direction::Forward){
                step_forward();
            }
            else if (dir == Direction::Backward) {
                step_backward();
            }
        }
    }

    int get_steps_count(){
        return steps_count;
    }

    void step_forward(){

        High(dir_pin);

        High(step_pin);
        delayMicroseconds(step_duration_us/2);
        Low(step_pin);
        delayMicroseconds(step_duration_us/2);

        this->steps_count++;
    }

    void step_backward(){

        Low(dir_pin);

        High(step_pin);
        delayMicroseconds(step_duration_us/2);
        Low(step_pin);
        delayMicroseconds(step_duration_us/2);

        this->steps_count--;
    }
*/

};

#endif