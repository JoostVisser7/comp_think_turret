String received_message = "";
bool message_complete = false;

void setup() {
  Serial.begin(110);
  Serial.flush();
  
  for (int i = 2; i <= 8; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
}

void read_buffer() {
  while (Serial.available() > 0) {
    digitalWrite(2, HIGH);
    int incoming_char = Serial.read();

    if (incoming_char == 1) {
      received_message = "";
      message_complete = true;
      digitalWrite(7, HIGH);
    }

    else if (incoming_char == 4) {
      message_complete = true;
      digitalWrite(8, HIGH);
    }
    
    else {
      received_message += char(incoming_char);
    }
  }
}


void loop() {
  read_buffer();
  if (message_complete) {
    Serial.print(received_message);
    message_complete = false;
  }
}
