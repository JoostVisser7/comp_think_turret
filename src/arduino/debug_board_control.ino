#include <LiquidCrystal.h>

// LCD pinout and setup
constexpr int rs = 2,
              en = 3,
              d4 = 6,
              d5 = 7,
              d6 = 8,
              d7 = 9;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// LED pinout
constexpr int LED1 = 11,
              LED2 = 12;

// Display text on debug LCD
void print_lcd(String payload, bool clear_previous = true) {
  if (clear_previous) {
    lcd.clear();          // clear screen
    lcd.setCursor(0, 0);  // reset cursor
  }
  lcd.print(payload);     // display payload
}

void setup() {
  // Initialize serial port
  Serial.begin(9600);   // set baud rate
  Serial.flush();       // clear buffer

  // Initialize debug LCD
  lcd.begin(16, 2);     // LCD has a 16x2 character matrix

  // Initialize debug LEDs
  pinMode(LED1, OUTPUT);
  pinMode(LED2, OUTPUT);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, LOW);
}

void loop() {
  // put your main code here, to run repeatedly:
    print_lcd("Hello, world!");
    delay(1000);
}
