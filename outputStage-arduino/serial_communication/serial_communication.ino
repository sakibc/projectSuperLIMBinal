#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver();

#define SERVOMIN 150
#define SERVOMAX 600

#define SYNNUM 8  // number of synergies

uint16_t synergies[SYNNUM];

uint16_t readUnsignedInt() {
  uint8_t dataBuffer[2];
  Serial.readBytes(dataBuffer,2);
  return (dataBuffer[0] << 8) | dataBuffer[1];
}

int getPulseLength(int deg) {
  // Convert from degrees to pulse length in ticks
  return map(deg, 0, 180, SERVOMIN, SERVOMAX);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Serial OK");

  servos.begin();
  servos.setPWMFreq(60);

  delay(10);
}

void loop() {
  for (uint8_t i = 0; i < SYNNUM; i++) {
    synergies[i] = readUnsignedInt();
  }
  // Serial.println(synergies[0]);
  
  int servoPos = map(synergies[0],0,1000,0,180);
  // Serial.println(servoPos);
  for (int i = 0; i < 5; i++)
  servos.setPWM(i,0,getPulseLength(servoPos));
}

