// Based off of the Girino Arduino oscilloscope project
// http://www.instructables.com/id/Girino-Fast-Arduino-Oscilloscope/

#include "inputStage-arduino.h"

volatile bool adcDone;
volatile uint8_t adcBuffer0[64];  //use double-buffering, so ADC ISR
volatile uint8_t adcBuffer1[64];  //doesn't need to be paused while
volatile uint8_t adcCounter;      //transmitting full buffer
volatile uint8_t currentBuffer;

void setup() {
  Serial.begin(500000); //any slower and the poor arduino can't keep up...
  Serial.println("Serial OK. Initializing...");

  DIDR0  = B11111111;
  ADMUX  = B01000000;
  ADCSRA = B11111101;
  ADCSRB = B00000000;
  
  memset((void*)adcBuffer0,0,sizeof(adcBuffer0));
  memset((void*)adcBuffer1,0,sizeof(adcBuffer1));
  
  currentBuffer = 0;
  adcCounter = 0;
  sei();
}

void loop() {
  if (adcCounter == 64) {
    adcCounter = 0;
    switch(currentBuffer) {
      case 0:
        currentBuffer = 1;
        Serial.write((uint8_t*) adcBuffer0,64);
        break;
      case 1:
        currentBuffer = 0;
        Serial.write((uint8_t*) adcBuffer1,64);
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

