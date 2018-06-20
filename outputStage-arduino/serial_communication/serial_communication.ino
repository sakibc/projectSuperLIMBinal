#include <Servo.h>

uint16_t syn0;
int servoPos = 0;
Servo myServo;

uint16_t readUnsignedInt() {
  uint8_t dataBuffer[2];
  Serial.readBytes(dataBuffer,2);
  return (dataBuffer[0] << 8) | dataBuffer[1];
}
 
void setup() {
  myServo.attach(3);
  Serial.begin(115200);
  myServo.write(servoPos);
  Serial.println("Serial OK");
}

void loop() {
  syn0 = readUnsignedInt();
  
  // if (Serial.available() >= 2){ //some data is available!!!
  //   syn0 = Serial.read(); //let's grab it
  //   syn1 = Serial.read();
  //   Serial.print(syn0,HEX);
  //   Serial.println(syn1,HEX);
  servoPos = map(syn0,0,1000,0,180);
  myServo.write(servoPos);
  // }
}

