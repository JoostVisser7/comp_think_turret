#include <Servo.h>

/*
 * Configuration of global constants
 */
constexpr int hor_servo_home = 90,
              hor_servo_min_angle = 0,
              hor_servo_max_angle = 170,
              hor_servo_pin = 3,

              ver_servo_home = 90,
              ver_servo_min_angle = 70,
              ver_servo_max_angle = 110,
              ver_servo_pin = 4,

              tri_servo_cold = 25,
              tri_servo_hot = 80,
              tri_servo_pin = 5,
              tri_servo_delay = 1000,

              baud_rate = 9600,
              serial_timeout = 100;


/*
 * Initialisation of global variables
 */
int hor_servo_target_angle,
    ver_servo_target_angle;

bool triggered;

Servo hor_servo,
      ver_servo,
      tri_servo;


/*
 * Operational code
 */
int clamp_angle(int current, int adjustment, int min, int max){
  // Make sure the new target angle does not exceed allowable values
  if (current + adjustment > max) {
    return max;
  }
  else if (current + adjustment < min) {
    return min;
  }
  return (current + adjustment);
}

void adjust_rotation(char axis, int adjustment) {
  // Write a new target angle for a given axis
  switch(axis){
    case 'x':
      hor_servo_target_angle = clamp_angle(
        hor_servo_target_angle,
        adjustment,
        hor_servo_min_angle,
        hor_servo_max_angle
      );
      break;
    case 'y':
      ver_servo_target_angle = clamp_angle(
        ver_servo_target_angle,
        adjustment,
        ver_servo_min_angle,
        ver_servo_max_angle
      );
      break;
  }
}

void message_parser(String message) {
  // rotation commands are of the format r(+|-)xx,(+|-)yy
  if (message[0] == 'r') {
    int separator = message.indexOf(',');

    String x_str = message.substring(1, separator),
           y_str = message.substring(separator + 1);

    int dx = x_str.toInt(),
        dy = y_str.toInt();

    adjust_rotation('x', dx);
    adjust_rotation('y', dy);

  }
  // trigger commands start with the letter t
  else if (message == "trigger") {
    triggered = true;
  }

  else if (message == "home") {
    hor_servo_target_angle = hor_servo_home;
    ver_servo_target_angle = ver_servo_home;
  }
}

void setup() {
  Serial.begin(baud_rate);
  Serial.setTimeout(serial_timeout);

  hor_servo.attach(hor_servo_pin);
  ver_servo.attach(ver_servo_pin);
  tri_servo.attach(tri_servo_pin);
  hor_servo.write(hor_servo_home);
  ver_servo.write(ver_servo_home);
  tri_servo.write(tri_servo_cold);

  hor_servo_target_angle = hor_servo_home;
  ver_servo_target_angle = ver_servo_home;
  triggered = false;

  Serial.println("ready");
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    
    Serial.println(ver_servo_target_angle);
    message_parser(message);   // interpret message and change appropriate globals
    Serial.println(ver_servo_target_angle);

    if (triggered) {    // pull trigger
      tri_servo.write(tri_servo_hot);
      delay(tri_servo_delay);
      tri_servo.write(tri_servo_cold);
      triggered = false;
    }

    else {    // 
      hor_servo.write(hor_servo_target_angle);
      ver_servo.write(ver_servo_target_angle);
    }
    Serial.println("ready");     // let PC know the arduino is ready for next command
  }
}