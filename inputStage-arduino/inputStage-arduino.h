// Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
//
// Based off of the Girino Arduino oscilloscope project
// Girino Copyright 2012 Cristiano Lino Fontana
//
// http://www.instructables.com/id/Girino-Fast-Arduino-Oscilloscope/

#include <Arduino.h>

#define BAUDRATE 500000

#define ADCBUFFERSIZE 64 //same size as write buffer, at 1 byte per value

#define ELEC0 0 //electrode pin numbers
#define ELEC1 1
#define ELEC2 2
#define ELEC3 3

// Helper macros /////////////////////////////////

// Defines for setting and clearing register bits
#ifndef cbi
#define cbi(sfr, bit) (_SFR_BYTE(sfr) &= ~_BV(bit))
#endif
#ifndef sbi
#define sbi(sfr, bit) (_SFR_BYTE(sfr) |= _BV(bit))
#endif
