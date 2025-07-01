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

# --- CONFIG ---
GEMINI_API_KEY = "AIzaSyAyGquNFvp1NyObrLohnm8pcIryAS4_bTY"
FIREBASE_DB_URL = "https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app/"
FIREBASE_CRED_FILE = "firebase_key.json"


# --- FLASK SETUP ---
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# --- FIREBASE INIT ---
try:
    cred = credentials.Certificate(FIREBASE_CRED_FILE)
    firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_DB_URL})
    print("✅ Firebase initialized successfully")
except Exception as e:
    print(f"❌ Firebase initialization failed: {e}")
    exit(1)

# --- TTS INIT ---
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Speech rate
tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

def speak(text: str):
    """Speak the given text using pyttsx3"""
    print(f"🔊 Speaking: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def send_firebase_command(device: str, command: str, value=None):
    """Send command to Firebase Realtime Database"""
    try:
        timestamp = datetime.now().isoformat()
        
        if device in ["lights", "fan", "party"]:
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
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
  "intent": "device_control" | "sensor_query" | "emergency" | "general_chat" | "unknown",
  "response": "natural reply to user",
  "actions": [
    {{
      "device": "fan" | "lights" | "buzzer" | "party",
      "command": "on" | "off" | "trigger",
      "value": true | false | duration in ms (for buzzer)
    }}
  ]
}}

Special commands:
- For device control, use "on"/"off" commands (not "turn_on"/"turn_off")
- For emergency/alert, trigger buzzer
- For casual conversation, use general_chat intent

Command: "{command}"
Respond only with valid JSON and nothing else.
"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # 🔧 Remove Markdown code fences if present
        if raw_text.startswith("```") and raw_text.endswith("```"):
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
model = None

def get_whisper_model():
    """Load Whisper model with error handling"""
    global model
    if model is None:
        try:
            print("📥 Loading Whisper model...")
            model = whisper.load_model("base")  # Change to "tiny" if needed
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            print("🔄 Trying to load 'tiny' model instead...")
            try:
                model = whisper.load_model("tiny")
                print("✅ Whisper 'tiny' model loaded successfully")
            except Exception as e2:
                print(f"❌ Failed to load any Whisper model: {e2}")
                model = None
    return model

def record_audio(filename="live.wav", duration=10):
    """Records audio from mic and saves as a WAV file."""
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 16000

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    print(f"\n🎙️ Recording for {duration} seconds...")

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

def transcribe_audio(file_path="live.wav") -> str:
    """Transcribes audio using Whisper."""
    try:
        print("🔁 Transcribing...")
        whisper_model = get_whisper_model()
        if whisper_model is None:
            print("❌ No Whisper model available")
            return ""
        
        result = whisper_model.transcribe(file_path)
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



def parse_command(command: str) -> dict:
    """Enhanced command parsing with Firebase integration"""
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

def process_text_command(text_command: str):
    """Process a text command and return results"""
    if not text_command.strip():
        return None
    
    print(f"\n📝 Processing text command: {text_command}")
    result = parse_command(text_command)
    
    print(f"🧠 Intent: {result['intent']}")
    print(f"💬 Response: {result['response']}")
    print(f"⚙️ Actions: {result.get('actions', [])}")
    
    if result.get('firebase_success'):
        print("✅ Firebase commands executed successfully")
    else:
        print("❌ Some Firebase commands failed")
    
    # Speak the response
    speak(result['response'])
    return result

def process_voice_command(duration=3):
    """Process a voice command and return results"""
    print(f"\n🎙️ Recording for {duration} seconds...")
    audio_file = record_audio(duration=duration)
    text = transcribe_audio(audio_file)
    
    if text:
        return process_text_command(text)
    else:
        print("🤷 No command detected. Try again.")
        return None

def main():
    print("🔊 VoiceOps Assistant with Firebase")
    print(f"🔥 Connected to Firebase: {FIREBASE_DB_URL}")
    print("\n" + "="*60)
    print("📋 Try commands like:")
    print("  • 'Turn on the fan' or 'Fan on'")
    print("  • 'Turn off the lights' or 'Lights off'")
    print("  • 'Turn on party mode' or 'Party on'")
    print("  • 'Emergency alert' or 'Trigger buzzer'")
    print("="*60)
    
    # Check command line arguments
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--api':
        print("\n🌐 Starting API Server Mode (for frontend)")
        print("🚀 Server running on http://127.0.0.1:5001")
        print("🌍 Frontend can now connect to the assistant!")
        print("📝 API Endpoints available:")
        print("  • GET  /health - Health check")
        print("  • POST /api/voice/process - Process text commands")
        print("  • POST /api/voice/listen - Voice listening")
        print("  • POST /api/devices/control - Direct device control")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            app.run(host='127.0.0.1', port=5001, debug=False)
        except KeyboardInterrupt:
            print("\n👋 API Server stopped.")
    else:
        print("\n🎯 CLI Mode - Interactive Voice Assistant")
        print("💡 Tip: Run with '--api' flag to start web server for frontend")
        
        try:
            while True:
                print("\n🎯 Choose input method:")
                print("1. Type 'text' for text command")
                print("2. Type 'voice' for voice command")
                print("3. Type 'quit' to exit")
                print("4. Or directly type a command")
                
                user_input = input("\n💭 Your choice/command: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Exiting VoiceOps Assistant.")
                    break
                elif user_input.lower() in ['voice', 'v']:
                    print("\nPrepare to speak your command...")
                    time.sleep(1)
                    process_voice_command(duration=3)
                elif user_input.lower() in ['text', 't']:
                    text_command = input("\n📝 Enter your command: ").strip()
                    if text_command:
                        process_text_command(text_command)
                elif user_input:
                    # Direct command input
                    process_text_command(user_input)
                else:
                    print("⚠️ Please enter a valid option or command.")
                
                time.sleep(0.5)
        
        except KeyboardInterrupt:
            print("\n👋 Exiting VoiceOps Assistant.")
        except Exception as e:
            print(f"\n❌ Error: {e}")

# --- FLASK API ENDPOINTS ---
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the frontend"""
    whisper_status = model is not None
    firebase_status = True  # Already initialized
    tts_status = True  # Already initialized
    
    return jsonify({
        'status': 'healthy',
        'service': 'VoiceOps Assistant API',
        'timestamp': datetime.now().isoformat(),
        'firebase_connected': firebase_status,
        'whisper_loaded': whisper_status,
        'tts_available': tts_status
    })

@app.route('/api/voice/process', methods=['POST'])
def api_process_text_command():
    """Process text command via API"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({'success': False, 'error': 'Command is required'}), 400
        
        command = data['command'].strip()
        speak_response = data.get('speak_response', False)
        
        if not command:
            return jsonify({'success': False, 'error': 'Command cannot be empty'}), 400
        
        # Process the command
        result = parse_command(command)
        
        # Speak response if requested
        if speak_response and result.get('response'):
            speak(result['response'])
        
        return jsonify({
            'success': True,
            'command': command,
            'intent': result.get('intent'),
            'response': result.get('response'),
            'actions': result.get('actions', []),
            'firebase_success': result.get('firebase_success', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/listen', methods=['POST'])
def api_listen_voice_command():
    """Listen for voice command via API"""
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 3)
        speak_response = data.get('speak_response', False)
        
        # Ensure duration is within bounds
        duration = max(1, min(duration, 10))
        
        # Record and transcribe
        audio_file = record_audio(duration=duration)
        text = transcribe_audio(audio_file)
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No speech detected',
                'timestamp': datetime.now().isoformat()
            })
        
        # Process the command
        result = parse_command(text)
        
        # Speak response if requested
        if speak_response and result.get('response'):
            speak(result['response'])
        
        return jsonify({
            'success': True,
            'command': text,
            'intent': result.get('intent'),
            'response': result.get('response'),
            'actions': result.get('actions', []),
            'firebase_success': result.get('firebase_success', False),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/devices/control', methods=['POST'])
def api_control_device():
    """Direct device control via API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Request data required'}), 400
        
        device = data.get('device')
        command = data.get('command')
        value = data.get('value')
        
        if not device or not command:
            return jsonify({'success': False, 'error': 'Device and command are required'}), 400
        
        # Send Firebase command
        success = send_firebase_command(device, command, value)
        
        return jsonify({
            'success': success,
            'device': device,
            'command': command,
            'value': value,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def run_flask_server():
    """Run Flask server in a separate thread"""
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

if __name__ == "__main__":
    main()