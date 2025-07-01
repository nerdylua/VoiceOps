# VoiceOps

VoiceOps is a modern, voice-enabled AI assistant designed for workspace and office automation. It integrates voice recognition, natural language understanding, IoT device control, and real-time notifications to create a seamless, intelligent environment. VoiceOps can be controlled via voice commands or Telegram, and is extensible for a variety of smart office scenarios.

---

## Features
- 🎤 **Voice Command Recognition** (multilingual, local language support)
- 🤖 **AI-Powered Assistant** (Gemini integration for natural conversation)
- 🏠 **IoT Device Control** (lights, fan, party mode, buzzer, servo, etc.)
- 📢 **Text-to-Speech Feedback** (speaks responses back to users)
- 🌐 **REST API** for integration with other systems
- 🔔 **Real-Time Alerts** for unsafe conditions or access control
- 🛡️ **Secure, Role-Based Access** (optional, extensible)

---

## Architecture
- **Backend:** Python (Flask, pyttsx3, speech_recognition, Gemini, Firebase)
- **Frontend:** Next.js (React, TypeScript, Tailwind CSS)
- **IoT/Edge:** ESP32/Arduino (for direct device control)
- **Database:** Firebase Realtime Database

---

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- Firebase project (for Realtime Database)
- (Optional) Telegram Bot Token

### Backend Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/nerdylua/VoiceOps.git
   cd voiceops/backend
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Firebase:**
   - Place your `firebase_key.json` in the backend directory.
   - Set your Firebase Realtime Database URL in the config section of `assistant.py`.
4. **Run the backend:**
   ```bash
   python assistant.py --api
   ```
   The server will start at `http://127.0.0.1:5001`.

### Frontend Setup
1. **Navigate to the frontend directory:**
   ```bash
   cd ../frontend
   ```
2. **Install dependencies:**
   ```bash
   pnpm install
   ```
3. **Run the frontend:**
   ```bash
   pnpm dev
   ```
   The app will be available at `http://localhost:3000`.

---

## Usage
- **Voice Commands:**
  - Use the web UI or CLI to issue commands like "Turn on the lights", "Fan off", or "Party mode on".
  - The assistant will speak back responses and control devices via Firebase.
- **API Endpoints:**
  - `POST /api/voice/process` — Process a text command
  - `POST /api/voice/listen` — Listen for a voice command
  - `POST /api/devices/control` — Direct device control
  - `GET /health` — Health check

#### Example API Request
```json
POST /api/voice/process
{
  "command": "Turn on the lights",
  "speak_response": true
}
```

---

## Project Structure
```
VoiceOps/
  backend/      # Python Flask backend, AI, TTS, device logic
  frontend/     # Next.js frontend, UI, QR login, dashboard
  esp/          # ESP32/Arduino code for IoT devices
```

---

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request


