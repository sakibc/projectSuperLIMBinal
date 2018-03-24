// Based off of the Girino Arduino oscilloscope project
// http://www.instructables.com/id/Girino-Fast-Arduino-Oscilloscope/

#include <Arduino.h>

#define BAUDRATE 115200

#define IN0 0
#define IN1 1
#define IN2 2
#define IN3 3

// Helper macros /////////////////////////////////

// Defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif
