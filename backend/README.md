# VoiceOps Flask Backend

AI-Driven Workspace Assistant Backend built with Flask, providing REST API endpoints for the frontend, ESP32 communication, Telegram bot integration, and voice command processing.

## 🚀 Features

- **REST API** - Complete API for frontend communication
- **ESP32 Integration** - Real-time sensor monitoring and device control
- **Firebase Database** - Cloud-based data storage and sync
- **Telegram Bot** - Remote command interface
- **Voice Processing** - AI-powered voice command recognition
- **Real-time Monitoring** - Live sensor data and activity tracking
- **Device Control** - Fan, lighting, and buzzer control
- **Automated Alerts** - Smart threshold-based notifications

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Firebase project with Realtime Database
- Telegram Bot Token (optional)
- ESP32 device (optional for development)

## 🛠️ Installation

1. **Clone the repository and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your configuration values.

## ⚙️ Configuration

### Required Environment Variables

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY="your-firebase-private-key"
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/

# ESP32 Configuration  
ESP32_WEBHOOK_URL=http://192.168.1.100
ESP32_API_KEY=your-esp32-api-key

# Security
SECRET_KEY=your-secret-key
ADMIN_PASSWORD=your-admin-password
```

### Optional Configuration

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Voice Processing APIs
OPENAI_API_KEY=your-openai-api-key
GOOGLE_SPEECH_API_KEY=your-google-speech-api-key
GEMINI_API_KEY=your-gemini-api-key

# Sensor Thresholds
TEMPERATURE_THRESHOLD_HIGH=30.0
HUMIDITY_THRESHOLD_HIGH=70.0
GAS_THRESHOLD_CRITICAL=0.8
```

## 🚀 Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
FLASK_ENV=production python app.py
```

The backend will start on `http://127.0.0.1:5000` by default.

## 📡 API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/guest` - Guest access

### Sensors
- `GET /api/sensors/current` - Get current sensor readings
- `GET /api/sensors/history` - Get historical sensor data

### Device Control
- `GET /api/devices/status` - Get device status
- `POST /api/devices/control` - Control devices

### Voice Commands
- `POST /api/voice/process` - Process voice commands

### System
- `GET /status` - System health check
- `GET /api/system/health` - Detailed system status

## 🔧 API Usage Examples

### Get Current Sensor Data
```bash
curl -X GET http://localhost:5000/api/sensors/current \
  -H "Authorization: Bearer your-jwt-token"
```

### Control Device
```bash
curl -X POST http://localhost:5000/api/devices/control \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "device": "fan",
    "action": "turn_on",
    "value": true
  }'
```

### Process Voice Command
```bash
curl -X POST http://localhost:5000/api/voice/process \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "text_command": "turn on the fan"
  }'
```

## 🏗️ Architecture

```
backend/
├── app.py                 # Main Flask application
├── config/
│   └── settings.py        # Configuration management
├── services/
│   ├── firebase_client.py # Firebase integration
│   ├── esp32_client.py    # ESP32 communication
│   ├── voice_processor.py # Voice command processing
│   └── telegram_bot.py    # Telegram bot service
├── routes/
│   ├── api_routes.py      # REST API endpoints
│   └── telegram_webhook.py # Telegram webhook
├── utils/
│   ├── logger.py          # Logging configuration
│   └── auth.py            # Authentication utilities
└── requirements.txt       # Python dependencies
```

## 🔐 Security

- JWT-based authentication
- API key validation for ESP32
- Environment variable configuration
- CORS protection
- Input validation and sanitization

## 📊 Monitoring & Logging

- Structured logging with rotation
- Real-time system health monitoring
- Activity tracking and audit logs
- Error handling and alerting

## 🤖 ESP32 Integration

The backend communicates with ESP32 via HTTP API:

### ESP32 Endpoints Expected:
- `GET /ping` - Health check
- `GET /api/sensors` - Sensor readings
- `GET /api/devices/status` - Device status
- `POST /api/devices/control` - Device control
- `POST /api/alert` - Alert notifications

### Example ESP32 Response:
```json
{
  "temperature": 24.5,
  "humidity": 45.0,
  "gas_level": 0.2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🔄 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black backend/
isort backend/
```

### Environment Setup
```bash
# Create development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

## 🚨 Troubleshooting

### Common Issues

1. **Firebase Connection Failed**
   - Check Firebase credentials in `.env`
   - Verify database URL format
   - Ensure Firebase project exists

2. **ESP32 Not Reachable**
   - Verify ESP32 IP address
   - Check network connectivity
   - Confirm ESP32 is running HTTP server

3. **Authentication Errors**
   - Check SECRET_KEY configuration
   - Verify token expiration
   - Confirm ADMIN_PASSWORD

### Debug Mode
Enable debug logging:
```bash
LOG_LEVEL=DEBUG python app.py
```

## 📝 License

This project is part of the VoiceOps system. See main project LICENSE for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For support and questions:
- Check the main project README
- Review API documentation
- Check system logs in `logs/voiceops.log` 