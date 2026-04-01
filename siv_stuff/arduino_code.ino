#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN 150
#define SERVOMAX 600
#define RELAY_PIN A0

int currentAngle[5] = {90, 120, 120, 85, 90};

// ----------------------------
int angleToPulse(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

// ----------------------------
void moveServoSlow(int channel, int targetAngle) {

  int stepDelay = 20;
  int current = currentAngle[channel];

  if (targetAngle > current) {
    for (int a = current; a <= targetAngle; a++) {
      pwm.setPWM(channel, 0, angleToPulse(a));
      delay(stepDelay);
    }
  } else {
    for (int a = current; a >= targetAngle; a--) {
      pwm.setPWM(channel, 0, angleToPulse(a));
      delay(stepDelay);
    }
  }

  currentAngle[channel] = targetAngle;
}

// ----------------------------
void setup() {
  Serial.begin(9600);

  pwm.begin();
  pwm.setPWMFreq(50);
  delay(10);

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // OFF

  for (int i = 0; i < 5; i++) {
    pwm.setPWM(i, 0, angleToPulse(currentAngle[i]));
  }

  Serial.println("READY");
}

// ----------------------------
void loop() {

  if (Serial.available()) {

    String input = Serial.readStringUntil('\n');
    input.trim();

    // 🔥 RELAY CONTROL
    if (input == "on") {
      digitalWrite(RELAY_PIN, LOW);
      Serial.println("Relay ON");
      return;
    }

    if (input == "off") {
      digitalWrite(RELAY_PIN, HIGH);
      Serial.println("Relay OFF");
      return;
    }

    // 🔥 SERVO CONTROL
    int servo, angle;

    if (sscanf(input.c_str(), "%d,%d", &servo, &angle) == 2) {

      if (servo >= 0 && servo < 5) {

        angle = constrain(angle, 0, 180);

        moveServoSlow(servo, angle);

        Serial.print("S");
        Serial.print(servo);
        Serial.print("=");
        Serial.println(angle);

      } else {
        Serial.println("Invalid servo");
      }

    } else {
      Serial.println("Invalid command");
    }
  }
}