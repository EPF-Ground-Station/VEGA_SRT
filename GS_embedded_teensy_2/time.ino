#include <TimeLib.h>

time_t getTeensyTime() {
  return Teensy3Clock.get();
}
