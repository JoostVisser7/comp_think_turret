#include <Servo.h> 

Servo servo_horizontal; // servo object representing the MG 996R servo
Servo servo_vertical; // servo object representing the MG 996R servo


String receivedData = "";  // Store the incoming data as a string
int dx = 0, dy = 0, angle_horizontal = 0, angle_vertical = 0; , max_angle = 170, min_angle = -170       // Variables to hold parsed dx and dy values recieved from python and initialize the angles

void angle_adjustment_horizontal(dx) {
if (dx > 100){
  angle_horizontal += 10;
}
if (dx < -100){
  angle_horizontal -= 10;
}
if(50 < dx < 100){
  angle_horizontal += 5;
}
if(-50 > dx > -100){
  angle_horizontal -= 5;
}
if(10 < dx < 50 ){
  angle_horizontal += 3;
}
if(-10 > dx > -50 ){
  angle_horizontal -= 3;
}
    return angle_horizontal;  
}

void angle_adjustment_vertical(dy) {
if (dy > 100){
  angle_horizontal += 10;
}
if (dy < -100){
  angle_horizontal -= 10;
}
if(50 < dy < 100){
  angle_horizontal += 5;
}
if(-50 > dy > -100){
  angle_horizontal -= 5;
}
if(10 < dy < 50 ){
  angle_horizontal += 3;
}
if(-10 > dy > -50 ){
  angle_horizontal -= 3;
}
    return angle_vertical;  
}

bool readSerialData(int &dx, int &dy) {
    if (Serial.available()) {
        String receivedData = Serial.readStringUntil('\n');  // Read until newline
        int commaIndex = receivedData.indexOf(',');          // Find the comma

        if (commaIndex != -1) {  // If comma is found
            // Extract and convert dx and dy from the string
            dx = receivedData.substring(0, commaIndex).toInt();
            dy = receivedData.substring(commaIndex + 1).toInt();
            return true;  // Indicate successful read
        }
    }
    return false;  // No data or invalid format
}


void setup() {
  Serial.begin(9600);
  servo_horizontal.attach(3); // servo is wired to Arduino on digital pin 3
  servo_horizontal.attach(4); // servo is wired to Arduino on digital pin 4
}

void loop() {

readSerialData(dx, dy)


angle_adjustment_horizontal ()
angle_adjustment_vertical ()

servo_horizontal.write(angle_horizontal);
servo_vertical.write(angle_vertical);
if (angle_horizontal > max_angle)
  angle_horizontal  = max_angle;
}
if (angle_horizontal < min_angle)
  angle_horizontal  = min_angle;
}
if (angle_vertical > max_angle)
  angle_vertical  = max_angle;
}
if (angle_vertical < min_angle)
  angle_vertical  = min_angle;
}