#include <Servo.h>

Servo servo;
constexpr int SERVO_PIN = 2;

void setup() {
  // put your setup code here, to run once:
  pinMode(SERVO_PIN, OUTPUT);
  servo.attach(SERVO_PIN);
  servo.write(25);
  delay(10000);
  servo.write(80);
  delay(200);
  servo.write(25);
}

void loop() {
  // put your main code here, to run repeatedly:

}