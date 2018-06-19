#include <Servo.h>

int c = 0;
int syn = 0;
Servo myServo;
 
void setup() {
  myServo.attach(3);
  Serial.begin(115200);
  myServo.write(0);
  while (!Serial){
    ;
  }
  Serial.println("Serial OK");
  }

void loop() {
  if (Serial.available() > 0){
    c = Serial.parseInt();
    syn = map(c, 0, 255, 0, 180);
    myServo.write(syn);
    Serial.println(syn);
  }
}

