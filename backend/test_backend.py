#!/usr/bin/env python3
"""
Simple test script for VoiceOps Flask Backend
Tests basic functionality without external dependencies
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_backend():
    """Test basic backend functionality"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing VoiceOps Flask Backend")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['service']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Health check failed - is the server running? {e}")
        return False
    
    # Test 2: System status
    print("\n2. Testing system status endpoint...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System status: {data['system_health']}")
            print(f"   Services: {data['services']}")
        else:
            print(f"❌ System status failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ System status failed: {e}")
    
    # Test 3: API endpoints (these might require auth)
    print("\n3. Testing API endpoints...")
    
    # Test sensor data endpoint
    try:
        response = requests.get(f"{base_url}/api/sensors/current")
        if response.status_code in [200, 401]:  # 401 is expected without auth
            print("✅ Sensor endpoint accessible")
        else:
            print(f"❌ Sensor endpoint error: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Sensor endpoint failed: {e}")
    
    # Test device status endpoint
    try:
        response = requests.get(f"{base_url}/api/devices/status")
        if response.status_code in [200, 401]:  # 401 is expected without auth
            print("✅ Device status endpoint accessible")
        else:
            print(f"❌ Device status endpoint error: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Device status endpoint failed: {e}")
    
    print("\n✅ Basic backend tests completed!")
    print("\nNext steps:")
    print("1. Configure your .env file with Firebase and other credentials")
    print("2. Set up ESP32 device communication")
    print("3. Configure Telegram bot (optional)")
    print("4. Test with the Next.js frontend")
    
    return True

def show_endpoints():
    """Show available API endpoints"""
    print("\n📡 Available API Endpoints:")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/", "Health check"),
        ("GET", "/status", "System status"),
        ("POST", "/api/auth/login", "User authentication"),
        ("POST", "/api/auth/guest", "Guest authentication"),
        ("GET", "/api/sensors/current", "Current sensor data"),
        ("GET", "/api/devices/status", "Device status"),
        ("POST", "/api/devices/control", "Control devices"),
        ("POST", "/api/voice/process", "Process voice commands"),
        ("POST", "/telegram/webhook", "Telegram webhook"),
        ("POST", "/telegram/send_message", "Send Telegram message")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"{method:6} {endpoint:25} - {description}")

if __name__ == "__main__":
    print("VoiceOps Flask Backend Test Script")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--endpoints":
        show_endpoints()
    else:
        print("\n⚠️  Make sure the Flask backend is running before testing!")
        print("Run: python app.py")
        print("\nPress Enter to continue with tests or Ctrl+C to cancel...")
        
        try:
            input()
            test_backend()
        except KeyboardInterrupt:
            print("\n\nTest cancelled by user.")
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
    
    print("\nFor endpoint information, run: python test_backend.py --endpoints") 