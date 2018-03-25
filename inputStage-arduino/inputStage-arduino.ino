// Copyright 2018 Sakib Chowdhury and Claudia Lutfallah
//
// Based off of the Girino Arduino oscilloscope project
// Girino Copyright 2012 Cristiano Lino Fontana
//
// http://www.instructables.com/id/Girino-Fast-Arduino-Oscilloscope/

#include "inputStage-arduino.h"

volatile bool adcDone;
volatile uint8_t adcBuffer0[ADCBUFFERSIZE];  //use double-buffering, so ADC ISR
volatile uint8_t adcBuffer1[ADCBUFFERSIZE];  //doesn't need to be paused while
volatile uint8_t adcCounter;                 //transmitting full buffer
volatile uint8_t currentBuffer;

void setup() {
  Serial.begin(BAUDRATE); //any slower than 500000 and the poor arduino can't keep up...
  Serial.println("Serial OK. Initializing...");

  DIDR0  = B11111111; //disable digital inputs to reduce noise
  ADMUX  = B01000000; //select channel 0
  ADCSRA = B11111101; //prescale of 32 for 37kS/s
  ADCSRB = B00000000;
  
  memset((void*)adcBuffer0,0,sizeof(adcBuffer0)); //clear buffers
  memset((void*)adcBuffer1,0,sizeof(adcBuffer1));
  
  currentBuffer = 0;
  adcCounter = 0;
  sei();
}

void loop() {
  if (adcCounter == ADCBUFFERSIZE) {
    adcCounter = 0;
    switch(currentBuffer) { //swap active buffer and transmit the finished one
      case 0:
        currentBuffer = 1;
        Serial.write((uint8_t*) adcBuffer0,ADCBUFFERSIZE);
        break;
      case 1:
        currentBuffer = 0;
        Serial.write((uint8_t*) adcBuffer1,ADCBUFFERSIZE);
        break;
    }
    Serial.println("\nDONE"); //Cycle Complete
  }
}

ISR(ADC_vect) {
  switch(currentBuffer) {
    case 0:
      adcBuffer0[adcCounter] = ADCH;
      break;
    case 1:
      adcBuffer1[adcCounter] = ADCH;
      break;
  }
  adcCounter += 1;
}

