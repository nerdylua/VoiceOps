"""
VoiceOps Flask Backend
AI-Driven Workspace Assistant with Voice & Telegram Interface

Main application file handling:
- REST API for frontend
- Telegram bot integration  
- ESP32 device communication
- Voice command processing
- Firebase database operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import logging
from threading import Thread

# Import our custom modules
from config.settings import Config
from services.telegram_bot import TelegramBot
from services.esp32_client import ESP32Client
from services.voice_processor import VoiceProcessor
from services.firebase_client import FirebaseClient
from routes.api_routes import api_bp
from routes.telegram_webhook import telegram_bp
from utils.logger import setup_logger

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Setup logging
logger = setup_logger()

# Initialize services
firebase_client = FirebaseClient()
esp32_client = ESP32Client()
voice_processor = VoiceProcessor()
telegram_bot = TelegramBot()

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(telegram_bp, url_prefix='/telegram')

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VoiceOps Backend',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def system_status():
    """Get system status including all connected services"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'services': {
            'flask': 'running',
            'firebase': firebase_client.is_connected(),
            'esp32': esp32_client.is_connected(),
            'telegram_bot': telegram_bot.is_running(),
            'voice_processor': voice_processor.is_available()
        },
        'system_health': 'healthy'
    }
    
    # Check if any critical services are down
    critical_services = ['firebase', 'esp32']
    for service in critical_services:
        if not status['services'][service]:
            status['system_health'] = 'degraded'
            break
    
    return jsonify(status)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

def initialize_services():
    """Initialize all services in background threads"""
    logger.info("Initializing VoiceOps services...")
    
    # Initialize Firebase connection
    try:
        firebase_client.initialize()
        logger.info("Firebase client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
    
    # Initialize ESP32 connection
    try:
        esp32_client.initialize()
        logger.info("ESP32 client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize ESP32: {e}")
    
    # Initialize Telegram bot
    try:
        telegram_bot.initialize()
        logger.info("Telegram bot initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {e}")
    
    # Initialize voice processor
    try:
        voice_processor.initialize()
        logger.info("Voice processor initialized")
    except Exception as e:
        logger.error(f"Failed to initialize voice processor: {e}")

if __name__ == '__main__':
    # Initialize services
    initialize_services()
    
    # Start Flask app
    logger.info("Starting VoiceOps Flask Backend...")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    ) 