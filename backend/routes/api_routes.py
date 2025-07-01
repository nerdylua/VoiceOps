"""
API Routes for VoiceOps Backend
REST API endpoints for frontend communication
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import json
import logging
import time
from functools import wraps

from services.firebase_client import FirebaseClient
from services.esp32_client import ESP32Client
from services.voice_processor import VoiceProcessor
from utils.auth import validate_auth, generate_auth_token, generate_jwt_token
from config.settings import Config

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

# Initialize services
firebase_client = FirebaseClient()
esp32_client = ESP32Client()
voice_processor = VoiceProcessor()

def auth_required(f):
    """Decorator to require authentication for protected endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not Config.AUTH_ENABLED:
            return f(*args, **kwargs)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        if not validate_auth(token):
            return jsonify({'error': 'Invalid authentication token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Authentication Routes
@api_bp.route('/auth/login', methods=['POST'])
def login():
    """QR-based authentication endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # For QR authentication, we expect the QR data
        qr_data = data.get('qrData')
        
        if not qr_data:
            return jsonify({'error': 'QR data required'}), 400
        
        # Parse QR data
        try:
            auth_data = json.loads(qr_data)
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid QR data format'}), 400
        
        # Validate required fields
        required_fields = ['userId', 'userName', 'signature', 'timestamp']
        for field in required_fields:
            if field not in auth_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check expiration
        if 'expiresAt' in auth_data:
            if time.time() * 1000 > auth_data['expiresAt']:
                return jsonify({'error': 'QR code has expired'}), 401
        
        # Validate signature (accept static and demo signatures)
        valid_signatures = ['sig_', 'demo_signature_', 'static_signature_voiceops_auth_2024']
        if not any(auth_data['signature'].startswith(sig) or auth_data['signature'] == sig for sig in valid_signatures):
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Generate JWT token
        token = generate_jwt_token(auth_data['userId'], auth_data['userName'])
        
        return jsonify({
            'success': True,
            'message': 'Authentication successful',
            'user': {
                'id': auth_data['userId'],
                'name': auth_data['userName'],
                'type': 'user'
            },
            'token': token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 500

# Guest authentication removed - QR-only authentication now

# Sensor Data Routes
@api_bp.route('/sensors/current', methods=['GET'])
@auth_required
def get_current_sensor_data():
    """Get current sensor readings"""
    # Mock data for now
    sensor_data = {
        'temperature': 24.5,
        'humidity': 45.0,
        'gas_level': 0.2,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': sensor_data
    })

@api_bp.route('/sensors/history', methods=['GET'])
@auth_required
def get_sensor_history():
    """Get historical sensor data"""
    try:
        # Get query parameters
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # Calculate time range
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get historical data from Firebase
        history = firebase_client.get_sensor_history(start_time, end_time, limit)
        
        return jsonify({
            'success': True,
            'data': history,
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': hours
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting sensor history: {e}")
        return jsonify({'error': 'Failed to retrieve sensor history'}), 500

# Device Control Routes
@api_bp.route('/devices/status', methods=['GET'])
@auth_required
def get_device_status():
    """Get current device status"""
    device_status = {
        'fan': False,
        'light': True,
        'buzzer': False,
        'system_status': 'active',
        'last_update': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'data': device_status
    })

@api_bp.route('/devices/control', methods=['POST'])
@auth_required
def control_device():
    """Control a device"""
    data = request.get_json()
    device = data.get('device')
    action = data.get('action')
    
    return jsonify({
        'success': True,
        'device': device,
        'action': action,
        'timestamp': datetime.now().isoformat()
    })

# Voice Command Routes
@api_bp.route('/voice/process', methods=['POST'])
@auth_required
def process_voice_command():
    """Process voice command from audio file or text"""
    try:
        data = request.get_json()
        
        if 'audio_data' in data:
            # Process audio data
            text_command = voice_processor.speech_to_text(data['audio_data'])
        elif 'text_command' in data:
            # Use provided text command
            text_command = data['text_command']
        else:
            return jsonify({'error': 'No audio data or text command provided'}), 400
        
        # Process the command with AI
        response = voice_processor.process_command(text_command)
        
        # Execute any device actions
        if response.get('actions'):
            for action in response['actions']:
                esp32_client.control_device(
                    action['device'],
                    action['command'],
                    action.get('value', True)
                )
        
        # Log command to Firebase
        firebase_client.log_voice_command(text_command, response)
        
        return jsonify({
            'success': True,
            'command': text_command,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        return jsonify({'error': 'Failed to process voice command'}), 500

# Activity and Logs Routes
@api_bp.route('/activity/recent', methods=['GET'])
@auth_required
def get_recent_activity():
    """Get recent system activity"""
    try:
        limit = request.args.get('limit', 20, type=int)
        hours = request.args.get('hours', 24, type=int)
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        activity = firebase_client.get_recent_activity(start_time, end_time, limit)
        
        return jsonify({
            'success': True,
            'data': activity,
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify({'error': 'Failed to retrieve activity'}), 500

# System Information Routes
@api_bp.route('/system/health', methods=['GET'])
def get_system_health():
    """Get system health status"""
    try:
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'services': {
                'firebase': firebase_client.is_connected(),
                'esp32': esp32_client.is_connected(),
                'voice_processor': voice_processor.is_available()
            },
            'sensor_thresholds': {
                'temperature_high': Config.TEMPERATURE_THRESHOLD_HIGH,
                'temperature_low': Config.TEMPERATURE_THRESHOLD_LOW,
                'humidity_high': Config.HUMIDITY_THRESHOLD_HIGH,
                'humidity_low': Config.HUMIDITY_THRESHOLD_LOW,
                'gas_critical': Config.GAS_THRESHOLD_CRITICAL,
                'gas_warning': Config.GAS_THRESHOLD_WARNING
            },
            'automation': {
                'auto_fan': Config.AUTO_FAN_ENABLED,
                'auto_alert': Config.AUTO_ALERT_ENABLED
            }
        }
        
        # Determine overall health
        all_services_up = all(health_status['services'].values())
        health_status['overall_status'] = 'healthy' if all_services_up else 'degraded'
        
        return jsonify({
            'success': True,
            'data': health_status
        })
    
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        return jsonify({'error': 'Failed to retrieve system health'}), 500

@api_bp.route('/system/config', methods=['GET'])
@auth_required
def get_system_config():
    """Get system configuration (non-sensitive data only)"""
    try:
        config_data = {
            'automation': {
                'auto_fan_enabled': Config.AUTO_FAN_ENABLED,
                'auto_alert_enabled': Config.AUTO_ALERT_ENABLED,
                'data_logging_interval': Config.DATA_LOGGING_INTERVAL
            },
            'thresholds': {
                'temperature_high': Config.TEMPERATURE_THRESHOLD_HIGH,
                'temperature_low': Config.TEMPERATURE_THRESHOLD_LOW,
                'humidity_high': Config.HUMIDITY_THRESHOLD_HIGH,
                'humidity_low': Config.HUMIDITY_THRESHOLD_LOW,
                'gas_critical': Config.GAS_THRESHOLD_CRITICAL,
                'gas_warning': Config.GAS_THRESHOLD_WARNING
            },
            'voice_service': Config.VOICE_RECOGNITION_SERVICE,
            'esp32_timeout': Config.ESP32_TIMEOUT
        }
        
        return jsonify({
            'success': True,
            'data': config_data
        })
    
    except Exception as e:
        logger.error(f"Error getting system config: {e}")
        return jsonify({'error': 'Failed to retrieve system config'}), 500 