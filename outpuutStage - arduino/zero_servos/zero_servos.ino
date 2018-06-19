#include <Servo.h>

Servo myservo;

int pos = 0;

void setup()
{
  myservo.attach(3);
  myservo.write(0);
}

void loop()
{
  myservo.write(0);
}
