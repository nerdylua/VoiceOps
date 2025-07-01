import pyaudio
import wave
import whisper
import time
import os
import json
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import pyttsx3
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import tempfile
import base64

# --- CONFIG ---
GEMINI_API_KEY = "AIzaSyDrOTwbid-eW_PfoZkzAH_AJPJEwdu91HE"
FIREBASE_DB_URL = "https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app/"
FIREBASE_CRED_FILE = "firebase_key.json"
PASSWORD = "open"

# Flask app for API mode
app = Flask(_name_)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Global variables
is_firebase_initialized = False
tts_engine = None
whisper_model = None

# --- FIREBASE INIT ---
def initialize_firebase():
    global is_firebase_initialized
    if not is_firebase_initialized:
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(FIREBASE_CRED_FILE)
                firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
            print("✅ Firebase initialized successfully")
            is_firebase_initialized = True
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            is_firebase_initialized = False

# --- TTS INIT ---
def initialize_tts():
    global tts_engine
    if tts_engine is None:
        try:
            tts_engine = pyttsx3.init()
            tts_engine.setProperty('rate', 150)  # Speech rate
            tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            print("✅ TTS initialized successfully")
        except Exception as e:
            print(f"❌ TTS initialization failed: {e}")
            tts_engine = None

def speak(text: str):
    """Speak the given text using pyttsx3"""
    try:
        if tts_engine:
            print(f"🔊 Speaking: {text}")
            tts_engine.say(text)
            tts_engine.runAndWait()
    except Exception as e:
        print(f"❌ TTS failed: {e}")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def send_firebase_command(device: str, command: str, value=None):
    """Send command to Firebase Realtime Database"""
    try:
        if not is_firebase_initialized:
            return False
            
        timestamp = datetime.now().isoformat()
        
        if device in ["light", "fan"]:
            # Send device control commands
            db.reference(f"/commands/{device}").set(command)
            print(f"🔥 Firebase: {device} -> {command}")
            
        elif device == "buzzer" and command == "trigger":
            # Send buzzer trigger with duration
            db.reference("/commands/buzzer").set({
                "status": "trigger",
                "duration": value or 3000,
                "timestamp": timestamp
            })
            print(f"🔥 Firebase: buzzer triggered for {value}ms")
            
        # Log the command
        db.reference("/logs").push({
            "device": device,
            "command": command,
            "value": value,
            "timestamp": timestamp
        })
        
        return True
    except Exception as e:
        print(f"❌ Firebase command failed: {e}")
        return False

def gemini_friendly_response(user_input: str) -> str:
    """
    Use Gemini to generate a friendly, expressive reply to the user.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""You're a cheerful, friendly home assistant. Be expressive, human-like, and playful, but keep it short and clear.

User said: "{user_input}"
Respond in a way that makes them smile 😄"""

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        return "I'm having a bit of a brain freeze. Try again in a moment!"

def gemini_map_command(command: str) -> dict:
    """Use Gemini to map natural voice command to structured JSON intent"""

    prompt = f"""
You are a smart home assistant. Interpret the user's voice command and convert it into a JSON response in this format:

{{
  "intent": "device_control" | "sensor_query" | "emergency" | "password_access" | "general_chat" | "unknown",
  "response": "natural reply to user",
  "actions": [
    {{
      "device": "fan" | "light" | "buzzer",
      "command": "on" | "off" | "trigger",
      "value": true | false | duration in ms (for buzzer)
    }}
  ]
}}

Special commands:
- If user says "open" (password), respond with password_access intent
- For device control, use "on"/"off" commands (not "turn_on"/"turn_off")
- For emergency/alert, trigger buzzer
- For casual conversation, use general_chat intent

Command: "{command}"
Respond only with valid JSON and nothing else.
"""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # 🔧 Remove Markdown code fences if present
        if raw_text.startswith("") and raw_text.endswith(""):
            lines = raw_text.splitlines()
            raw_text = "\n".join(line for line in lines if not line.startswith("```")).strip()

        print("🔹 Gemini raw output (cleaned):\n", raw_text)

        return json.loads(raw_text)

    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        return {
            "intent": "unknown",
            "response": "Sorry, I couldn't process that.",
            "actions": []
        }

# Load Whisper model lazily to avoid SSL issues on import
def get_whisper_model():
    """Load Whisper model with error handling"""
    global whisper_model
    if whisper_model is None:
        try:
            print("📥 Loading Whisper model...")
            whisper_model = whisper.load_model("base")  # Change to "tiny" if needed
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            print("🔄 Trying to load 'tiny' model instead...")
            try:
                whisper_model = whisper.load_model("tiny")
                print("✅ Whisper 'tiny' model loaded successfully")
            except Exception as e2:
                print(f"❌ Failed to load any Whisper model: {e2}")
                whisper_model = None
    return whisper_model

def record_audio(filename="live.wav", duration=3):
    """Records audio from mic and saves as a WAV file."""
    try:
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 16000

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        print(f"\n🎙 Recording for {duration} seconds...")

        frames = [stream.read(chunk) for _ in range(int(rate / chunk * duration))]

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        
        return filename
    except Exception as e:
        print(f"❌ Audio recording failed: {e}")
        return None

def transcribe_audio(file_path="live.wav") -> str:
    """Transcribes audio using Whisper."""
    try:
        print("🔁 Transcribing...")
        model = get_whisper_model()
        if model is None:
            print("❌ No Whisper model available")
            return ""
        
        result = model.transcribe(file_path)
        text = result["text"].strip()
        print(f"📝 Transcribed: {text}")
        return text
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return ""

def execute_actions(actions: list) -> bool:
    """Execute the parsed actions by sending commands to Firebase"""
    success = True
    
    for action in actions:
        device = action.get("device")
        command = action.get("command")
        value = action.get("value")
        
        if device and command:
            if not send_firebase_command(device, command, value):
                success = False
    
    return success

def handle_password_access():
    """Handle password access - turn on all devices"""
    print("🔐 Password access granted!")
    
    # Turn on both light and fan
    send_firebase_command("light", "on")
    send_firebase_command("fan", "on")
    
    return "Welcome! Turning on all devices for you."

def parse_command(command: str) -> dict:
    """Enhanced command parsing with Firebase integration"""
    cmd = command.lower()
    
    # Check for password first
    if PASSWORD in cmd:
        response = handle_password_access()
        return {
            "intent": "password_access", 
            "response": response, 
            "actions": [],
            "firebase_success": True
        }
    
    # Use Gemini for intelligent parsing
    result = gemini_map_command(command)
    
    # Execute actions if any
    firebase_success = True
    if result.get("actions"):
        firebase_success = execute_actions(result["actions"])
    
    # Handle special intents
    if result["intent"] == "general_chat":
        # For general conversation, get a friendly response
        result["response"] = gemini_friendly_response(command)
    
    result["firebase_success"] = firebase_success
    return result

# --- API ENDPOINTS ---

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'VoiceOps Assistant',
        'timestamp': datetime.now().isoformat(),
        'firebase_connected': is_firebase_initialized,
        'whisper_loaded': whisper_model is not None,
        'tts_available': tts_engine is not None
    })

@app.route('/api/voice/listen', methods=['POST'])
def listen_voice_command():
    """Listen for voice command with configurable duration"""
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 3)  # Default 3 seconds
        speak_response = data.get('speak_response', False)
        
        # Ensure duration is within reasonable bounds
        duration = max(1, min(duration, 10))
        
        # Record audio
        audio_file = record_audio(duration=duration)
        if not audio_file:
            return jsonify({
                'success': False,
                'error': 'Failed to record audio'
            }), 500
        
        # Transcribe audio
        text = transcribe_audio(audio_file)
        
        # Clean up audio file
        try:
            os.remove(audio_file)
        except:
            pass
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No speech detected'
            }), 400
        
        # Process command
        result = parse_command(text)
        
        # Speak response if requested
        if speak_response and result.get('response'):
            threading.Thread(target=speak, args=(result['response'],)).start()
        
        return jsonify({
            'success': True,
            'command': text,
            'intent': result['intent'],
            'response': result['response'],
            'actions': result.get('actions', []),
            'firebase_success': result.get('firebase_success', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Voice listen failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/voice/process', methods=['POST'])
def process_text_command():
    """Process text command"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({
                'success': False,
                'error': 'No command provided'
            }), 400
        
        command = data['command'].strip()
        speak_response = data.get('speak_response', False)
        
        if not command:
            return jsonify({
                'success': False,
                'error': 'Empty command'
            }), 400
        
        # Process command
        result = parse_command(command)
        
        # Speak response if requested
        if speak_response and result.get('response'):
            threading.Thread(target=speak, args=(result['response'],)).start()
        
        return jsonify({
            'success': True,
            'command': command,
            'intent': result['intent'],
            'response': result['response'],
            'actions': result.get('actions', []),
            'firebase_success': result.get('firebase_success', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Text command failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_continuous_mode():
    """Original continuous listening mode"""
    print("🔊 VoiceOps Assistant with Firebase Started (Ctrl+C to stop)")
    print(f"🔥 Connected to Firebase: {FIREBASE_DB_URL}")
    print(f"🔑 Password: '{PASSWORD}' to unlock all devices")
    
    try:
        while True:
            audio_file = record_audio(duration=3)
            if audio_file:
                text = transcribe_audio(audio_file)
                
                # Clean up audio file
                try:
                    os.remove(audio_file)
                except:
                    pass

                if text:
                    result = parse_command(text)
                    print(f"🧠 Intent: {result['intent']}")
                    print(f"💬 Response: {result['response']}")
                    print(f"⚙ Actions: {result.get('actions', [])}")
                    
                    if result.get('firebase_success'):
                        print("✅ Firebase commands executed successfully")
                    else:
                        print("❌ Some Firebase commands failed")
                    print()
                    
                    # Speak response
                    if result.get('response'):
                        speak(result['response'])
                else:
                    print("🤷 No command detected. Try again.\n")
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n👋 Exiting VoiceOps Assistant.")

def run_api_mode(host='127.0.0.1', port=5001):
    """Run as API service"""
    print("🚀 Starting VoiceOps Assistant API")
    print(f"🌐 Running on http://{host}:{port}")
    print("📝 Available endpoints:")
    print("  GET  /health              - Health check")
    print("  POST /api/voice/listen    - Listen for voice command")
    print("  POST /api/voice/process   - Process text command")
    print("=" * 50)
    
    app.run(host=host, port=port, debug=False, threaded=True)

def main():
    """Main function - choose between continuous or API mode"""
    import sys
    
    # Initialize services
    initialize_firebase()
    initialize_tts()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'api':
        # API mode
        host = sys.argv[2] if len(sys.argv) > 2 else '127.0.0.1'
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 5001
        run_api_mode(host, port)
    else:
        # Continuous mode
        run_continuous_mode()

if _name_ == "_main_":
    main()