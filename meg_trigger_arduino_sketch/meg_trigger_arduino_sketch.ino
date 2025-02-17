const int numPins = 8;  
const int outputPins[numPins] = {2, 3, 4, 5, 6, 7, 8, 9};  // 8 digital output pins

void setup() {
  Serial.begin(115200);  // Match baud rate with Python
  for (int i = 0; i < numPins; i++) {
    pinMode(outputPins[i], OUTPUT);
    digitalWrite(outputPins[i], LOW);  // Initialize to LOW
  }
}

void loop() {
  if (Serial.available()) {
    byte triggerValue = Serial.read();  // Read 8-bit trigger value
    for (int i = 0; i < numPins; i++) {
      digitalWrite(outputPins[i], (triggerValue >> i) & 1);  // Set each pin according to bit state
    }
  }
}