"""
Simplified VoiceOps Flask Backend for Testing
Basic version without external dependencies
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Basic configuration
app.config['SECRET_KEY'] = 'test-secret-key'

@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VoiceOps Backend (Test Mode)',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/status')
def system_status():
    """Get system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'services': {
            'flask': True,
            'firebase': False,  # Not connected in test mode
            'esp32': False,     # Not connected in test mode
    
            'voice_processor': False
        },
        'system_health': 'healthy (test mode)'
    }
    
    return jsonify(status)

# Mock API routes for testing
@app.route('/api/sensors/current', methods=['GET'])
def get_current_sensor_data():
    """Get current sensor readings (mock data)"""
    sensor_data = {
        'temperature': 24.5,
        'humidity': 45.0,
        'gas_level': 0.2,
        'timestamp': datetime.now().isoformat(),
        'source': 'mock'
    }
    
    return jsonify({
        'success': True,
        'data': sensor_data
    })

@app.route('/api/devices/status', methods=['GET'])
def get_device_status():
    """Get current device status (mock data)"""
    device_status = {
        'fan': False,
        'light': True,
        'buzzer': False,
        'system_status': 'active',
        'last_update': datetime.now().isoformat(),
        'source': 'mock'
    }
    
    return jsonify({
        'success': True,
        'data': device_status
    })

@app.route('/api/devices/control', methods=['POST'])
def control_device():
    """Control a device (mock response)"""
    data = request.get_json()
    device = data.get('device') if data else 'unknown'
    action = data.get('action') if data else 'unknown'
    value = data.get('value', True) if data else True
    
    return jsonify({
        'success': True,
        'device': device,
        'action': action,
        'value': value,
        'timestamp': datetime.now().isoformat(),
        'mode': 'mock'
    })

@app.route('/api/voice/process', methods=['POST'])
def process_voice_command():
    """Process voice command (mock response)"""
    data = request.get_json()
    text_command = data.get('text_command', 'unknown command') if data else 'unknown command'
    
    # Simple mock response
    response = {
        'intent': 'mock',
        'response': f'Mock processing of: {text_command}',
        'actions': []
    }
    
    return jsonify({
        'success': True,
        'command': text_command,
        'response': response,
        'timestamp': datetime.now().isoformat(),
        'mode': 'mock'
    })

@app.route('/api/auth/login', methods=['POST'])
def qr_auth_login():
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
            import json
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
            import time
            if time.time() * 1000 > auth_data['expiresAt']:
                return jsonify({'error': 'Authentication expired'}), 401
        
        # Validate signature and user
        valid_signatures = ['static_signature_voiceops_auth_2024']
        if not any(auth_data['signature'] == sig for sig in valid_signatures):
            return jsonify({'error': 'Invalid signature'}), 401
            
        # Check if it's Mr. Nihaal's access
        if auth_data.get('userId') == 'nihaal_office_2025':
            user_name = 'Mr. Nihaal'
        else:
            user_name = auth_data.get('userName', 'Office User')
        
        # Generate simple token
        import base64
        token_data = f"{auth_data['userId']}:{user_name}:{datetime.now().isoformat()}"
        token = base64.b64encode(token_data.encode()).decode()
        
        return jsonify({
            'success': True,
            'message': f'Welcome {user_name}! Office systems activated.',
            'user': {
                'id': auth_data['userId'],
                'name': user_name,
                'type': 'office_user'
            },
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting VoiceOps Flask Backend (Test Mode)")
    print("=" * 50)
    print("Available endpoints:")
    print("GET  /                    - Health check")
    print("GET  /status              - System status")
    print("GET  /api/sensors/current - Mock sensor data")
    print("GET  /api/devices/status  - Mock device status")
    print("POST /api/devices/control - Mock device control")
    print("POST /api/voice/process   - Mock voice processing")
    print("POST /api/auth/login      - QR authentication")
    print("=" * 50)
    print("Server running at: http://127.0.0.1:5000")
    print("Frontend should connect to this URL")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    ) 