"""
Configuration settings for VoiceOps Backend
Handles environment variables and application configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'voiceops-secret-key-change-in-production')
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', '')
    FIREBASE_PRIVATE_KEY_ID = os.getenv('FIREBASE_PRIVATE_KEY_ID', '')
    FIREBASE_PRIVATE_KEY = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
    FIREBASE_CLIENT_EMAIL = os.getenv('FIREBASE_CLIENT_EMAIL', '')
    FIREBASE_CLIENT_ID = os.getenv('FIREBASE_CLIENT_ID', '')
    FIREBASE_DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL', '')
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')  # Admin chat ID
    
    # ESP32 Configuration
    ESP32_WEBHOOK_URL = os.getenv('ESP32_WEBHOOK_URL', 'http://192.168.1.100')  # ESP32 IP
    ESP32_API_KEY = os.getenv('ESP32_API_KEY', 'esp32-api-key')
    ESP32_TIMEOUT = int(os.getenv('ESP32_TIMEOUT', 10))  # seconds
    
    # Voice Processing Configuration
    GOOGLE_SPEECH_API_KEY = os.getenv('GOOGLE_SPEECH_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    VOICE_RECOGNITION_SERVICE = os.getenv('VOICE_RECOGNITION_SERVICE', 'google')  # google, openai, gemini
    
    # Sensor Thresholds
    TEMPERATURE_THRESHOLD_HIGH = float(os.getenv('TEMPERATURE_THRESHOLD_HIGH', 30.0))  # Celsius
    TEMPERATURE_THRESHOLD_LOW = float(os.getenv('TEMPERATURE_THRESHOLD_LOW', 15.0))   # Celsius
    HUMIDITY_THRESHOLD_HIGH = float(os.getenv('HUMIDITY_THRESHOLD_HIGH', 70.0))       # Percentage
    HUMIDITY_THRESHOLD_LOW = float(os.getenv('HUMIDITY_THRESHOLD_LOW', 30.0))         # Percentage
    GAS_THRESHOLD_CRITICAL = float(os.getenv('GAS_THRESHOLD_CRITICAL', 0.8))          # MQ-2 reading
    GAS_THRESHOLD_WARNING = float(os.getenv('GAS_THRESHOLD_WARNING', 0.5))            # MQ-2 reading
    
    # Automation Settings
    AUTO_FAN_ENABLED = os.getenv('AUTO_FAN_ENABLED', 'True').lower() == 'true'
    AUTO_ALERT_ENABLED = os.getenv('AUTO_ALERT_ENABLED', 'True').lower() == 'true'
    DATA_LOGGING_INTERVAL = int(os.getenv('DATA_LOGGING_INTERVAL', 60))  # seconds
    
    # Security Settings
    AUTH_ENABLED = os.getenv('AUTH_ENABLED', 'True').lower() == 'true'
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'voiceops123')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # seconds
    
    # Database Settings
    SQLITE_DATABASE_PATH = os.getenv('SQLITE_DATABASE_PATH', 'data/voiceops.db')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/voiceops.log')
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', 10485760))  # 10MB in bytes
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    @staticmethod
    def validate_config():
        """Validate required configuration variables"""
        required_vars = [
            'FIREBASE_PROJECT_ID',
            'TELEGRAM_BOT_TOKEN',
            'ESP32_WEBHOOK_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(Config, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    AUTH_ENABLED = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    AUTH_ENABLED = False
    SQLITE_DATABASE_PATH = ':memory:'

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'default')
    return config_map.get(env, DevelopmentConfig) 