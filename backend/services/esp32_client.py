"""
ESP32 Client Service for VoiceOps
Handles communication with ESP32 device for sensor data and device control
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
import time

from config.settings import Config

logger = logging.getLogger(__name__)

class ESP32Client:
    """ESP32 communication client for VoiceOps"""
    
    def __init__(self):
        self.base_url = Config.ESP32_WEBHOOK_URL
        self.api_key = Config.ESP32_API_KEY
        self.timeout = Config.ESP32_TIMEOUT
        self.connected = False
        self.last_ping = None
        
    def initialize(self):
        """Initialize ESP32 connection and test connectivity"""
        try:
            # Test connection with ping
            if self.ping():
                self.connected = True
                logger.info(f"ESP32 client initialized successfully at {self.base_url}")
            else:
                self.connected = False
                logger.warning(f"ESP32 not reachable at {self.base_url}")
                
        except Exception as e:
            logger.error(f"Failed to initialize ESP32 client: {e}")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if ESP32 is connected"""
        # Check if we've pinged recently
        if self.last_ping:
            time_since_ping = time.time() - self.last_ping
            if time_since_ping > 30:  # Re-ping every 30 seconds
                return self.ping()
        
        return self.connected
    
    def ping(self) -> bool:
        """Ping ESP32 to check connectivity"""
        try:
            response = requests.get(
                f"{self.base_url}/ping",
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.connected = True
                self.last_ping = time.time()
                return True
            else:
                self.connected = False
                return False
                
        except requests.RequestException as e:
            logger.debug(f"ESP32 ping failed: {e}")
            self.connected = False
            return False
    
    def get_sensor_data(self) -> Optional[Dict[str, Any]]:
        """Get current sensor readings from ESP32"""
        try:
            if not self.is_connected():
                return None
            
            response = requests.get(
                f"{self.base_url}/api/sensors",
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Add timestamp
                data['timestamp'] = datetime.now().isoformat()
                data['source'] = 'esp32'
                
                logger.debug(f"Retrieved sensor data: {data}")
                return data
            else:
                logger.warning(f"Failed to get sensor data. Status: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error getting sensor data from ESP32: {e}")
            self.connected = False
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from ESP32: {e}")
            return None
    
    def get_device_status(self) -> Optional[Dict[str, Any]]:
        """Get current device status from ESP32"""
        try:
            if not self.is_connected():
                return None
            
            response = requests.get(
                f"{self.base_url}/api/devices/status",
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                data['last_update'] = datetime.now().isoformat()
                data['source'] = 'esp32'
                
                logger.debug(f"Retrieved device status: {data}")
                return data
            else:
                logger.warning(f"Failed to get device status. Status: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error getting device status from ESP32: {e}")
            self.connected = False
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from ESP32: {e}")
            return None
    
    def control_device(self, device: str, action: str, value: Any = True) -> bool:
        """Send device control command to ESP32"""
        try:
            if not self.is_connected():
                logger.warning("ESP32 not connected, cannot control device")
                return False
            
            payload = {
                'device': device,
                'action': action,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/api/devices/control",
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    logger.info(f"Device control successful: {device} {action} {value}")
                    return True
                else:
                    logger.warning(f"Device control failed: {result.get('error', 'Unknown error')}")
                    return False
            else:
                logger.warning(f"Device control request failed. Status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error controlling device via ESP32: {e}")
            self.connected = False
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from ESP32: {e}")
            return False
    
    def send_alert(self, alert_type: str, message: str, severity: str = "warning") -> bool:
        """Send alert to ESP32 (buzzer, LED indicators)"""
        try:
            if not self.is_connected():
                return False
            
            payload = {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.base_url}/api/alert",
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"Alert sent to ESP32: {alert_type} - {message}")
                return True
            else:
                logger.warning(f"Failed to send alert. Status: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error sending alert to ESP32: {e}")
            self.connected = False
            return False
    
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """Get ESP32 system information"""
        try:
            if not self.is_connected():
                return None
            
            response = requests.get(
                f"{self.base_url}/api/system/info",
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Retrieved ESP32 system info: {data}")
                return data
            else:
                return None
                
        except requests.RequestException as e:
            logger.debug(f"Error getting ESP32 system info: {e}")
            return None
    
    def restart_esp32(self) -> bool:
        """Send restart command to ESP32"""
        try:
            if not self.is_connected():
                return False
            
            response = requests.post(
                f"{self.base_url}/api/system/restart",
                headers={"X-API-Key": self.api_key},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info("ESP32 restart command sent")
                self.connected = False  # Will need to reconnect
                return True
            else:
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error sending restart command to ESP32: {e}")
            return False
    
    def update_config(self, config_data: Dict[str, Any]) -> bool:
        """Update ESP32 configuration"""
        try:
            if not self.is_connected():
                return False
            
            response = requests.post(
                f"{self.base_url}/api/config/update",
                json=config_data,
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info("ESP32 configuration updated")
                return True
            else:
                return False
                
        except requests.RequestException as e:
            logger.error(f"Error updating ESP32 config: {e}")
            return False
    
    # Convenience methods for specific device controls
    def turn_fan_on(self) -> bool:
        """Turn fan on"""
        return self.control_device('fan', 'turn_on', True)
    
    def turn_fan_off(self) -> bool:
        """Turn fan off"""
        return self.control_device('fan', 'turn_off', False)
    
    def toggle_light(self) -> bool:
        """Toggle light status"""
        return self.control_device('light', 'toggle')
    
    def set_light(self, state: bool) -> bool:
        """Set light state"""
        action = 'turn_on' if state else 'turn_off'
        return self.control_device('light', action, state)
    
    def trigger_buzzer(self, duration: int = 1000) -> bool:
        """Trigger buzzer for specified duration (ms)"""
        return self.control_device('buzzer', 'trigger', duration)
    
    def emergency_alert(self) -> bool:
        """Trigger emergency alert (buzzer + red LED)"""
        return self.send_alert('emergency', 'Emergency alert triggered', 'critical') 