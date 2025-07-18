import pyaudio
import wave
import speech_recognition as sr
import time
import json
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import pyttsx3
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import whisper

# --- CONFIG ---
GEMINI_API_KEY = "your_gemini_api_key"
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

# --- TTS FUNCTIONS ---

def speak_and_shutdown(text: str):
    """Speak using Windows SAPI directly to avoid run loop issues"""
    try:
        if text and text.strip():
            # Use Windows SAPI directly via COM interface
            import win32com.client
            sapi = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Set female voice if available
            voices = sapi.GetVoices()
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_name = voice.GetDescription().lower()
                if any(keyword in voice_name for keyword in ['female', 'woman', 'hazel', 'susan', 'samantha', 'victoria', 'fiona']):
                    sapi.Voice = voice
                    break
            
            sapi.Rate = 2
            sapi.Speak(text)
            
    except ImportError:
        # Fallback to pyttsx3 if win32com not available
        fallback_pyttsx3_speak(text)
    except Exception as e:
        print(f"❌ SAPI TTS failed: {e}")
        fallback_pyttsx3_speak(text)

def fallback_pyttsx3_speak(text: str):
    """Fallback to pyttsx3 if SAPI fails"""
    local_tts = None
    try:
        local_tts = pyttsx3.init()
        local_tts.setProperty('rate', 150)
        local_tts.setProperty('volume', 0.9)
        
        # Set female voice if available
        voices = local_tts.getProperty('voices')
        if len(voices) > 1:
            local_tts.setProperty('voice', voices[1].id)
        
        local_tts.say(text)
        local_tts.runAndWait()
        
    except Exception as e:
        print(f"❌ Fallback TTS failed: {e}")
    finally:
        if local_tts:
            try:
                local_tts.stop()
                del local_tts
            except:
                pass

def speak(text: str):
    """Start TTS in background thread"""
    if text and text.strip():
        tts_thread = threading.Thread(target=speak_and_shutdown, args=(text,), daemon=True)
        tts_thread.start()

# --- SPEECH RECOGNITION INIT ---
speech_recognizer = None
microphone = None

def initialize_speech_recognition():
    global speech_recognizer, microphone
    if speech_recognizer is None:
        try:
            speech_recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            with microphone as source:
                speech_recognizer.adjust_for_ambient_noise(source, duration=1)
            speech_recognizer.energy_threshold = 300
            speech_recognizer.dynamic_energy_threshold = True
            speech_recognizer.pause_threshold = 0.8
            speech_recognizer.phrase_threshold = 0.3
            print("✅ Speech recognition initialized")
        except Exception as e:
            print(f"❌ Speech recognition initialization failed: {e}")
            speech_recognizer = None
            microphone = None

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def send_firebase_command(device: str, command: str, value=None):
    """Send command to Firebase Realtime Database"""
    if device == 'light':
        device = 'lights'
    
    try:
        if device in ["lights", "fan", "party"]:
            db.reference(f"/commands/{device}").set(command)
            print(f"🔥 Firebase: {device} -> {command}")
        elif device == "buzzer" and command == "trigger":
            db.reference("/commands/buzzer").set({
                "status": "trigger",
                "duration": value or 3000,
                "timestamp": datetime.now().isoformat()
            })
            print(f"🔥 Firebase: buzzer triggered for {value or 3000}ms")
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
        
        prompt = f"""You're a cheerful, friendly home assistant. Be expressive, human-like, and playful, but keep it short and clear. Do not use any emojis, asterisks, markdown characters or underscores in your response.

User said: "{user_input}"
Respond in a way that makes them smile."""

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
- If the user says 'light' or 'lights', always map to the device key 'lights'.

Command: "{command}"
Respond only with valid JSON and nothing else.
"""

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Remove Markdown code fences if present
        if raw_text.startswith("```") and raw_text.endswith("```"):
            lines = raw_text.splitlines()
            raw_text = "\n".join(line for line in lines if not line.startswith("```")).strip()

        return json.loads(raw_text)

    except Exception as e:
        print(f"❌ Gemini failed: {e}")
        return {
            "intent": "unknown",
            "response": "Sorry, I couldn't process that.",
            "actions": []
        }

model = None

def get_whisper_model():
    """Load Whisper model with error handling"""
    global model
    if model is None:
        try:
            model = whisper.load_model("base")
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"❌ Failed to load Whisper model: {e}")
            try:
                model = whisper.load_model("tiny")
                print("✅ Whisper 'tiny' model loaded")
            except Exception as e2:
                print(f"❌ Failed to load any Whisper model: {e2}")
                model = None
    return model

def record_audio(filename="live.wav", duration=10):
    """Records audio from mic and saves as a WAV file"""
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    rate = 16000

    p = pyaudio.PyAudio()
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

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
    """Transcribes audio using Whisper"""
    try:
        whisper_model = get_whisper_model()
        if whisper_model is None:
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

def process_text_command(text_command: str, speak_response=True):
    if not text_command.strip():
        return None
    
    result = parse_command(text_command)
    if speak_response and result.get('response'):
        speak(result['response'])
    return result

def process_voice_command(duration=3, language_code='en-US', speak_response=True):
    print(f"🎙️ Listening for {duration} seconds...")
    # Try speech_recognition first
    text = listen_for_speech(duration=duration, language_code=language_code)
    if not text:
        # Fallback to Whisper
        audio_file = record_audio(duration=duration)
        text = transcribe_audio(audio_file)
    if text:
        return process_text_command(text, speak_response=speak_response)
    else:
        print("🤷 No command detected")
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
    import sys
    initialize_speech_recognition()
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
                    process_voice_command(duration=3, speak_response=True)
                elif user_input.lower() in ['text', 't']:
                    text_command = input("\n📝 Enter your command: ").strip()
                    if text_command:
                        process_text_command(text_command, speak_response=True)
                elif user_input:
                    process_text_command(user_input, speak_response=True)
                else:
                    print("⚠️ Please enter a valid option or command.")
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n👋 Exiting VoiceOps Assistant.")
        except Exception as e:
            print(f"\n❌ Error: {e}")

# --- SPEECH RECOGNITION (GOOGLE + SPHINX) ---
def listen_for_speech(duration=5, language_code='en-US'):
    """Listen for speech using speech_recognition library (Google + Sphinx fallback)"""
    try:
        if not speech_recognizer or not microphone:
            print("❌ Speech recognition not initialized")
            return ""
        print(f"🎙️ Listening for {duration} seconds...")
        with microphone as source:
            audio = speech_recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
        print("🔄 Processing speech...")
        # Try Google Speech Recognition first (multilingual)
        try:
            text = speech_recognizer.recognize_google(audio, language=language_code)
            print(f"📝 Google SR: {text}")
            return text
        except sr.UnknownValueError:
            print("❓ Google SR could not understand audio")
        except sr.RequestError as e:
            print(f"❌ Google SR error: {e}")
        # Fallback to offline Sphinx (English/local)
        try:
            text = speech_recognizer.recognize_sphinx(audio)
            print(f"📝 Sphinx SR: {text}")
            return text
        except sr.UnknownValueError:
            print("❓ Sphinx SR could not understand audio")
        except sr.RequestError as e:
            print(f"❌ Sphinx SR error: {e}")
        except Exception:
            print("❌ Sphinx not available")
        return ""
    except sr.WaitTimeoutError:
        print("⏰ Listening timeout - no speech detected")
        return ""
    except Exception as e:
        print(f"❌ Speech recognition failed: {e}")
        return ""

# --- FLASK API ENDPOINTS ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'VoiceOps Assistant API',
        'timestamp': datetime.now().isoformat(),
        'firebase_connected': True,
        'tts_available': True,
        'speech_recognition_ready': speech_recognizer is not None
    })

@app.route('/api/voice/process', methods=['POST'])
def api_process_text_command():
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({'success': False, 'error': 'Command is required'}), 400
        command = data['command'].strip()
        speak_response = data.get('speak_response', False)
        if not command:
            return jsonify({'success': False, 'error': 'Command cannot be empty'}), 400
        result = parse_command(command)
        
        # Prepare response first
        response_data = {
            'success': True,
            'command': command,
            'intent': result.get('intent'),
            'response': result.get('response'),
            'actions': result.get('actions', []),
            'firebase_success': result.get('firebase_success', False),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to TTS queue if requested
        if speak_response and result.get('response'):
            speak(result['response'])
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/voice/listen', methods=['POST'])
def api_listen_voice_command():
    try:
        data = request.get_json() or {}
        duration = data.get('duration', 3)
        speak_response = data.get('speak_response', False)
        language_code = data.get('language_code', 'en-US')
        duration = max(1, min(duration, 10))
        # Try speech_recognition first
        text = listen_for_speech(duration=duration, language_code=language_code)
        if not text:
            # Fallback to Whisper
            audio_file = record_audio(duration=duration)
            text = transcribe_audio(audio_file)
        if not text:
            return jsonify({
                'success': False,
                'error': 'No speech detected',
                'timestamp': datetime.now().isoformat()
            })
        result = parse_command(text)
        
        # Prepare response first
        response_data = {
            'success': True,
            'command': text,
            'intent': result.get('intent'),
            'response': result.get('response'),
            'actions': result.get('actions', []),
            'firebase_success': result.get('firebase_success', False),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to TTS queue if requested
        if speak_response and result.get('response'):
            speak(result['response'])
        
        return jsonify(response_data)
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



if __name__ == "__main__":
    main()