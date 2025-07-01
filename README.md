# VoiceOps

VoiceOps is a modern, voice-enabled AI assistant designed for workspace and office automation. It integrates voice recognition, natural language understanding, IoT device control, and real-time notifications to create a seamless, intelligent environment. VoiceOps can be controlled via voice commands or Telegram, and features QR code-based authentication for secure access.

---

## Features
- 🎤 **Voice Command Recognition** (multilingual, local language support)
- 🤖 **AI-Powered Assistant** (Gemini integration for natural conversation)
- 🏠 **IoT Device Control** (lights, fan, party mode, servo, buzzer, sensors)
- 📢 **Text-to-Speech Feedback** (speaks responses back to users)
- 🌐 **REST API** for integration with other systems
- 🔔 **Real-Time Alerts** for unsafe conditions or access control
- 🔐 **QR Code Authentication** (secure, password-less login)
- 🛡️ **Secure, Role-Based Access** (optional, extensible)
- 📱 **Responsive Web Interface** with modern UI

---

## Architecture
- **Backend:** Python (Flask, pyttsx3, speech_recognition, Gemini, Firebase)
- **Frontend:** Next.js (React, TypeScript, Tailwind CSS, QR Scanner)
- **IoT/Edge:** ESP32 (Arduino IDE, Firebase Client, device control)
- **Database:** Firebase Realtime Database
- **Authentication:** QR Code-based (html5-qrcode library)

---

## Hardware Components (ESP32)
- **💡 LEDs** - Normal lighting (pins 12-14) + Party LED (pin 15)
- **🌀 Stepper Fan** - Motor control (pins 16-19)
- **🔧 Servo Motor** - Door automation (pin 26)
- **🚨 Buzzer** - Alerts (pin 25)
- **📊 Sensors** - MQ2 (pin 34), DHT22 (pin 35)

---

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- Arduino IDE with ESP32 board support
- Firebase project (for Realtime Database)
- ESP32 development board

### 1. Firebase Setup
1. **Create Firebase Project:**
   - Go to [Firebase Console](https://console.firebase.google.com)
   - Create new project
   - Enable Realtime Database

2. **Configure Database Rules:**
   ```json
   {
     "rules": {
       "commands": {
         ".read": "auth != null",
         ".write": "auth != null"
       },
       "sensors": {
         ".read": "auth != null",
         ".write": "auth != null"
       }
     }
   }
   ```

3. **Get Database URL:**
   - Copy your database URL (e.g., `https://your-project.firebaseio.com/`)

### 2. Backend Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/nerdylua/VoiceOps.git
   cd VoiceOps/backend
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure assistant.py:**
   - Update Firebase database URL
   - Add your Gemini API key
   - Configure voice settings
4. **Run the backend:**
   ```bash
   python assistant.py --api
   ```
   The server will start at `http://127.0.0.1:5001`.

### 3. Frontend Setup
1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```
2. **Install dependencies:**
   ```bash
   pnpm install
   ```
3. **Configure Firebase:**
   - Update Firebase config in the frontend code
   - Ensure QR authentication is properly set up
4. **Run the frontend:**
   ```bash
   pnpm dev
   ```
   The app will be available at `http://localhost:3000`.

### 4. ESP32 Setup
1. **Install Libraries:** Firebase ESP Client, ESP32Servo (via Arduino IDE)
2. **Update WiFi/Firebase credentials** in `esp/esp32.ino`
3. **Wire components** according to pin assignments
4. **Upload code** to ESP32 board

---

## Firebase Database Structure
```json
{
  "commands": {
    "lights": "on/off",
    "fan": "on/off", 
    "party": "on/off",
    "servo": "on/off"
  },
  "sensors": {
    "gas_level": 0
  }
}
```

## Usage

### Voice Commands
- **"Turn on the lights"**, **"Start the fan"**, **"Party mode on"**, **"Open the door"**

### API Endpoints
- `POST /api/voice/process` — Process voice commands
- `POST /api/devices/control` — Direct device control
- `GET /health` — Health check

## Project Structure
```
VoiceOps/
├── backend/                 # Python Flask backend
│   ├── assistant.py        # Main AI assistant logic
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities and services
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
└── esp/                   # ESP32 Arduino code
    ├── esp32.ino         # Main ESP32 firmware
    └── pinconfig.txt     # Hardware pin assignments
```

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request