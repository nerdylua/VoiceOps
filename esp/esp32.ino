#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <Stepper.h>
#include <ESP32Servo.h>

// Wi-Fi credentials
#define WIFI_SSID "Neo7"
#define WIFI_PASSWORD "nihaalsp7"

// Firebase credentials
#define API_KEY "your_gemini_api_key"
#define DATABASE_URL "https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app/"
#define USER_EMAIL "testuser@abc.com"
#define USER_PASSWORD "12345678"

// Firebase objects
FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// Hardware pins - Normal LEDs
#define LED1_PIN 12
#define LED2_PIN 13
#define LED3_PIN 14

// Color changing LED (RGB/WS2812)
#define PARTY_LED_PIN 15

// Stepper motor pins
#define STEPPER_STEPS 2048
#define IN1 16
#define IN2 17
#define IN3 18
#define IN4 19

// Servo motor
#define SERVO_PIN 26
#define SERVO_OPEN_ANGLE 60
#define SERVO_CLOSE_ANGLE -10

// MQ2 Gas sensor, DHT22, and Buzzer
#define MQ2_PIN 34  // Analog pin for MQ2
#define DHT22_PIN 35  // Digital pin for DHT22
#define BUZZER_PIN 25  // Digital pin for buzzer

// Device instances
Stepper stepper(STEPPER_STEPS, IN1, IN2, IN3, IN4);
Servo doorServo;

// State variables
bool fanRunning = false;
unsigned long lastFirebaseCheck = 0;

// Timing intervals
#define FIREBASE_CHECK_INTERVAL 2000  // Check Firebase every 2 seconds

void setup() {
  Serial.begin(115200);
  Serial.println("🚀 VoiceOps ESP32 Starting...");

  // Setup pins
  setupPins();
  
  // Initialize devices
  initializeDevices();
  
  // Connect to Wi-Fi
  connectToWiFi();
  
  // Initialize Firebase
  initializeFirebase();
  
  Serial.println("✅ System Ready!");
}

void setupPins() {
  // Normal LEDs
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(LED3_PIN, OUTPUT);
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);
  digitalWrite(LED3_PIN, LOW);

  // Party LED (assuming RGB common cathode)
  pinMode(PARTY_LED_PIN, OUTPUT);
  digitalWrite(PARTY_LED_PIN, LOW);

  // Stepper motor pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // MQ2 sensor (analog input) - for namesake
  pinMode(MQ2_PIN, INPUT);

  // DHT22 sensor (digital input) - for namesake  
  pinMode(DHT22_PIN, INPUT);

  // Buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("📌 Pins configured");
}

void initializeDevices() {
  // Stepper motor speed
  stepper.setSpeed(10);  // RPM

  // Servo motor
  doorServo.attach(SERVO_PIN);
  doorServo.write(SERVO_CLOSE_ANGLE);  // Start with door closed

  // Test buzzer
  digitalWrite(BUZZER_PIN, HIGH);
  delay(100);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("🔧 Devices initialized");
}

void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("📡 Connecting to Wi-Fi");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    Serial.print(".");
    delay(500);
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ Wi-Fi Connected!");
    Serial.print("📍 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Wi-Fi Connection Failed!");
  }
}

void initializeFirebase() {
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);
  Serial.println("🔥 Firebase initialized");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check Firebase commands
  if (currentTime - lastFirebaseCheck >= FIREBASE_CHECK_INTERVAL) {
    checkFirebaseCommands();
    lastFirebaseCheck = currentTime;
  }
  
  delay(50);  // Small delay to prevent overwhelming the system
}

void checkFirebaseCommands() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ Wi-Fi disconnected, attempting reconnection...");
    connectToWiFi();
    return;
  }

  Serial.println("🔄 Polling Firebase...");

  // Check lights command
  if (Firebase.RTDB.getString(&fbdo, "/commands/lights")) {
    String lightState = fbdo.stringData();
    Serial.print("💡 Lights command: ");
    Serial.println(lightState);
    controlNormalLEDs(lightState);
  } else {
    Serial.println("❌ Failed to read lights command");
  }

  // Check fan command
  if (Firebase.RTDB.getString(&fbdo, "/commands/fan")) {
    String fanState = fbdo.stringData();
    Serial.print("🌀 Fan command: ");
    Serial.println(fanState);
    controlFan(fanState);
  } else {
    Serial.println("❌ Failed to read fan command");
  }

  // Check party command
  if (Firebase.RTDB.getString(&fbdo, "/commands/party")) {
    String partyState = fbdo.stringData();
    Serial.print("🎉 Party command: ");
    Serial.println(partyState);
    controlPartyMode(partyState);
  } else {
    Serial.println("❌ Failed to read party command");
  }

  // Check servo command
  if (Firebase.RTDB.getString(&fbdo, "/commands/servo")) {
    String servoState = fbdo.stringData();
    Serial.print("🔧 Servo command: ");
    Serial.println(servoState);
    controlServo(servoState);
  } else {
    Serial.println("❌ Failed to read servo command");
  }
}

void controlNormalLEDs(String state) {
  bool ledState = (state == "on");
  digitalWrite(LED1_PIN, ledState ? HIGH : LOW);
  digitalWrite(LED2_PIN, ledState ? HIGH : LOW);
  digitalWrite(LED3_PIN, ledState ? HIGH : LOW);
  Serial.println(ledState ? "💡 Normal LEDs ON" : "💡 Normal LEDs OFF");
}

void controlFan(String state) {
  if (state == "on" && !fanRunning) {
    fanRunning = true;
    stepper.step(512);  // Rotate forward 1/4 revolution
    Serial.println("🌀 Fan started (forward spin)");
  } else if (state == "off" && fanRunning) {
    fanRunning = false;
    releaseStepper();
  }
}

void controlPartyMode(String state) {
  bool ledState = (state == "on");
  digitalWrite(PARTY_LED_PIN, ledState ? HIGH : LOW);
  Serial.println(ledState ? "🎉 Party LED ON" : "🎉 Party LED OFF");
}

void controlServo(String state) {
  if (state == "on") {
    doorServo.write(SERVO_OPEN_ANGLE);
    Serial.println("🔧 Servo ON (door opened)");
  } else if (state == "off") {
    doorServo.write(SERVO_CLOSE_ANGLE);
    Serial.println("🔧 Servo OFF (door closed)");
  }
}

void releaseStepper() {
  // Cut power to coils to "release" the motor
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  Serial.println("🌀 Stepper coils de-energized (fan stopped)");
}