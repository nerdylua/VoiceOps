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

# --- CONFIG ---
GEMINI_API_KEY = "AIzaSyDrOTwbid-eW_PfoZkzAH_AJPJEwdu91HE"
FIREBASE_DB_URL = "https://iot-el-1842a-default-rtdb.asia-southeast1.firebasedatabase.app/"
FIREBASE_CRED_FILE = "firebase_key.json"
PASSWORD = "open"

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

def main():
    print("🔊 VoiceOps Assistant with Firebase Started (Ctrl+C to stop)")
    print(f"🔥 Connected to Firebase: {FIREBASE_DB_URL}")
    print(f"🔑 Password: '{PASSWORD}' to unlock all devices")
    
    try:
        while True:
            audio_file = record_audio(duration=3)
            text = transcribe_audio(audio_file)

            if text:
                result = parse_command(text)
                print(f"🧠 Intent: {result['intent']}")
                print(f"💬 Response: {result['response']}")
                print(f"⚙️ Actions: {result.get('actions', [])}")
                
                if result.get('firebase_success'):
                    print("✅ Firebase commands executed successfully")
                else:
                    print("❌ Some Firebase commands failed")
                print()
            else:
                print("🤷 No command detected. Try again.\n")
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n👋 Exiting VoiceOps Assistant.")

if __name__ == "__main__":
    main()