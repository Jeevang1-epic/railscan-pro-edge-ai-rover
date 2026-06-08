/*
  RailScan Pro - Arduino UNO L298N emergency STOP firmware.

  Prompt 2 V2 scope:
  - Keep motors safe by default.
  - Accept a serial STOP command from the Python host.
  - Latch emergency stop until the Arduino is reset.
*/

#include <Arduino.h>

// L298N pin mapping for Arduino UNO.
constexpr uint8_t LEFT_ENABLE_PWM = 5;   // ENA
constexpr uint8_t LEFT_IN1 = 7;          // IN1
constexpr uint8_t LEFT_IN2 = 8;          // IN2
constexpr uint8_t RIGHT_ENABLE_PWM = 6;  // ENB
constexpr uint8_t RIGHT_IN3 = 9;         // IN3
constexpr uint8_t RIGHT_IN4 = 10;        // IN4

// Serial protocol.
constexpr unsigned long SERIAL_BAUD_RATE = 115200;
constexpr char STOP_TOKEN[] = "STOP";
constexpr uint8_t STOP_TOKEN_LENGTH = 4;

// Safety: keep disabled unless wheels are lifted and direction is verified.
constexpr bool AUTO_START_MOTORS = false;
constexpr uint8_t DEFAULT_MOTOR_SPEED = 150;

bool emergencyStopLatched = false;
uint8_t stopParserIndex = 0;

void configurePins();
void configureSerial();
void driveForward(uint8_t speed);
void stopMotors();
void triggerEmergencyStop();
void processSerialInput();
bool updateStopParser(char incoming);

void setup() {
  configurePins();
  stopMotors();
  configureSerial();

  if (AUTO_START_MOTORS) {
    driveForward(DEFAULT_MOTOR_SPEED);
    Serial.println("AUTO_START_MOTORS_ENABLED");
  } else {
    Serial.println("AUTO_START_MOTORS_DISABLED");
  }
}

void loop() {
  processSerialInput();

  if (emergencyStopLatched) {
    stopMotors();
    return;
  }

  if (AUTO_START_MOTORS) {
    driveForward(DEFAULT_MOTOR_SPEED);
  }
}

void configurePins() {
  pinMode(LEFT_ENABLE_PWM, OUTPUT);
  pinMode(LEFT_IN1, OUTPUT);
  pinMode(LEFT_IN2, OUTPUT);
  pinMode(RIGHT_ENABLE_PWM, OUTPUT);
  pinMode(RIGHT_IN3, OUTPUT);
  pinMode(RIGHT_IN4, OUTPUT);
}

void configureSerial() {
  Serial.begin(SERIAL_BAUD_RATE);
  Serial.println("RAILSCAN_MOTOR_CONTROLLER_READY");
}

void processSerialInput() {
  while (Serial.available() > 0) {
    const char incoming = static_cast<char>(Serial.read());
    if (updateStopParser(incoming)) {
      triggerEmergencyStop();
    }
  }
}

bool updateStopParser(char incoming) {
  if (incoming >= 'a' && incoming <= 'z') {
    incoming = static_cast<char>(incoming - ('a' - 'A'));
  }

  // A single S is the production STOP command. The parser also accepts
  // "STOP" from Serial Monitor without using blocking reads or String.
  if (incoming == 'S') {
    stopParserIndex = 1;
    return true;
  }

  if (stopParserIndex > 0 && incoming == STOP_TOKEN[stopParserIndex]) {
    stopParserIndex++;
    if (stopParserIndex >= STOP_TOKEN_LENGTH) {
      stopParserIndex = 0;
      return true;
    }
    return false;
  }

  stopParserIndex = 0;
  return false;
}

void triggerEmergencyStop() {
  if (emergencyStopLatched) {
    return;
  }

  emergencyStopLatched = true;
  stopMotors();
  Serial.println("EMERGENCY_STOP_LATCHED");
}

void stopMotors() {
  analogWrite(LEFT_ENABLE_PWM, 0);
  analogWrite(RIGHT_ENABLE_PWM, 0);

  digitalWrite(LEFT_IN1, LOW);
  digitalWrite(LEFT_IN2, LOW);
  digitalWrite(RIGHT_IN3, LOW);
  digitalWrite(RIGHT_IN4, LOW);
}

void driveForward(uint8_t speed) {
  if (emergencyStopLatched) {
    stopMotors();
    return;
  }

  digitalWrite(LEFT_IN1, HIGH);
  digitalWrite(LEFT_IN2, LOW);
  digitalWrite(RIGHT_IN3, HIGH);
  digitalWrite(RIGHT_IN4, LOW);

  analogWrite(LEFT_ENABLE_PWM, speed);
  analogWrite(RIGHT_ENABLE_PWM, speed);
}
