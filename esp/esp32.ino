#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <Stepper.h>  // Stepper library

// Wi-Fi credentials
#define WIFI_SSID "Neo7"
#define WIFI_PASSWORD "nihaalsp7"

// Firebase credentials
#define API_KEY "AIzaSyBrslc-yG_jMFLqEO7Cfw5Bflmz8Y_oeJY"
#define DATABASE_URL "https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app/"
#define USER_EMAIL "testuser@abc.com"
#define USER_PASSWORD "12345678"

// Firebase objects
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Hardware pins
#define LED_PIN 4
#define STEPPER_STEPS 2048

#define IN1 16
#define IN2 17
#define IN3 18
#define IN4 19

// Stepper instance
Stepper stepper(STEPPER_STEPS, IN1, IN2, IN3, IN4);

void releaseStepper() {
  // Optional: cut power to coils to "release" the motor (free spin)
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  Serial.println("Stepper coils de-energized (fan stopped)");
}

void setup() {
  Serial.begin(115200);

  // Setup pins
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stepper.setSpeed(10);  // RPM

  // Wi-Fi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nWi-Fi Connected!");

  // Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("Firebase initialized.");
}

void loop() {
  Serial.println("Polling Firebase...");

  // LED control
  if (Firebase.RTDB.getString(&fbdo, "/commands/lights")) {
    String lightState = fbdo.stringData();
    Serial.print("Lights command: ");
    Serial.println(lightState);
    digitalWrite(LED_PIN, lightState == "on" ? HIGH : LOW);
  }

  // Fan (Stepper) control
  if (Firebase.RTDB.getString(&fbdo, "/commands/fan")) {
    String fanState = fbdo.stringData();
    Serial.print("Fan command: ");
    Serial.println(fanState);

    if (fanState == "on") {
      stepper.step(512);  // Rotate forward 1/4 revolution
      Serial.println("Fan running (forward spin)");
    } else if (fanState == "off") {
      releaseStepper();  // Stop + cut power to coils
    }
  }

  delay(2000);  // Poll delay
}
