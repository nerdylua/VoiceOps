"""
Firebase Client Service for VoiceOps
Handles Firebase database operations and real-time data sync
"""

import firebase_admin
from firebase_admin import credentials, db
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from config.settings import Config

logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebase database client for VoiceOps"""
    
    def __init__(self):
        self.app = None
        self.database = None
        self.connected = False
        
    def initialize(self):
        """Initialize Firebase connection"""
        try:
            # Create credentials from environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": Config.FIREBASE_PROJECT_ID,
                "private_key_id": Config.FIREBASE_PRIVATE_KEY_ID,
                "private_key": Config.FIREBASE_PRIVATE_KEY,
                "client_email": Config.FIREBASE_CLIENT_EMAIL,
                "client_id": Config.FIREBASE_CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            # Initialize Firebase app
            cred = credentials.Certificate(cred_dict)
            self.app = firebase_admin.initialize_app(cred, {
                'databaseURL': Config.FIREBASE_DATABASE_URL
            })
            
            # Get database reference
            self.database = db.reference('/')
            self.connected = True
            logger.info("Firebase client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.connected = False
            raise
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return self.connected and self.database is not None
    
    def store_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Store sensor data to Firebase"""
        try:
            if not self.is_connected():
                return False
            
            # Add timestamp if not present
            if 'timestamp' not in sensor_data:
                sensor_data['timestamp'] = datetime.now().isoformat()
            
            # Store in sensors collection
            sensors_ref = self.database.child('sensors')
            
            # Store current data
            sensors_ref.child('current').set(sensor_data)
            
            # Store in historical data with timestamp key
            timestamp_key = datetime.now().strftime('%Y%m%d_%H%M%S')
            sensors_ref.child('history').child(timestamp_key).set(sensor_data)
            
            logger.debug(f"Stored sensor data: {sensor_data}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store sensor data: {e}")
            return False
    
    def get_latest_sensor_data(self) -> Optional[Dict[str, Any]]:
        """Get latest sensor data from Firebase"""
        try:
            if not self.is_connected():
                return None
            
            current_ref = self.database.child('sensors/current')
            data = current_ref.get()
            
            return data if data else None
            
        except Exception as e:
            logger.error(f"Failed to get latest sensor data: {e}")
            return None
    
    def get_sensor_history(self, start_time: datetime, end_time: datetime, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical sensor data within time range"""
        try:
            if not self.is_connected():
                return []
            
            history_ref = self.database.child('sensors/history')
            
            # Convert datetime to timestamp keys for querying
            start_key = start_time.strftime('%Y%m%d_%H%M%S')
            end_key = end_time.strftime('%Y%m%d_%H%M%S')
            
            # Query historical data
            data = history_ref.order_by_key().start_at(start_key).end_at(end_key).limit_to_last(limit).get()
            
            if data:
                # Convert to list and sort by timestamp
                history_list = list(data.values())
                history_list.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                return history_list
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get sensor history: {e}")
            return []
    
    def log_device_action(self, device: str, action: str, value: Any) -> bool:
        """Log device control action"""
        try:
            if not self.is_connected():
                return False
            
            action_data = {
                'device': device,
                'action': action,
                'value': value,
                'timestamp': datetime.now().isoformat(),
                'type': 'device_control'
            }
            
            # Store in device_actions collection
            timestamp_key = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
            device_actions_ref = self.database.child('device_actions')
            device_actions_ref.child(timestamp_key).set(action_data)
            
            # Update device status
            device_status_ref = self.database.child('device_status')
            device_status_ref.child(device).set({
                'status': value,
                'last_action': action,
                'last_update': datetime.now().isoformat()
            })
            
            logger.info(f"Logged device action: {device} {action} {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log device action: {e}")
            return False
    
    def log_voice_command(self, command: str, response: Dict[str, Any]) -> bool:
        """Log voice command and AI response"""
        try:
            if not self.is_connected():
                return False
            
            command_data = {
                'command': command,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'type': 'voice_command'
            }
            
            # Store in voice_commands collection
            timestamp_key = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            voice_commands_ref = self.database.child('voice_commands')
            voice_commands_ref.child(timestamp_key).set(command_data)
            
            logger.info(f"Logged voice command: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log voice command: {e}")
            return False
    
    def log_telegram_message(self, message: str, chat_id: str, response: str) -> bool:
        """Log Telegram bot interaction"""
        try:
            if not self.is_connected():
                return False
            
            telegram_data = {
                'message': message,
                'chat_id': chat_id,
                'response': response,
                'timestamp': datetime.now().isoformat(),
                'type': 'telegram_message'
            }
            
            # Store in telegram_messages collection
            timestamp_key = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
            telegram_ref = self.database.child('telegram_messages')
            telegram_ref.child(timestamp_key).set(telegram_data)
            
            logger.info(f"Logged Telegram message: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log Telegram message: {e}")
            return False
    
    def get_recent_activity(self, start_time: datetime, end_time: datetime, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activity (all types combined)"""
        try:
            if not self.is_connected():
                return []
            
            all_activity = []
            
            # Get device actions
            device_actions = self._get_activity_by_type('device_actions', start_time, end_time, limit)
            all_activity.extend(device_actions)
            
            # Get voice commands
            voice_commands = self._get_activity_by_type('voice_commands', start_time, end_time, limit)
            all_activity.extend(voice_commands)
            
            # Get telegram messages
            telegram_messages = self._get_activity_by_type('telegram_messages', start_time, end_time, limit)
            all_activity.extend(telegram_messages)
            
            # Sort by timestamp and limit results
            all_activity.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            return all_activity[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recent activity: {e}")
            return []
    
    def _get_activity_by_type(self, collection: str, start_time: datetime, end_time: datetime, limit: int) -> List[Dict[str, Any]]:
        """Helper method to get activity by type"""
        try:
            collection_ref = self.database.child(collection)
            
            start_key = start_time.strftime('%Y%m%d_%H%M%S')
            end_key = end_time.strftime('%Y%m%d_%H%M%S')
            
            data = collection_ref.order_by_key().start_at(start_key).end_at(end_key).limit_to_last(limit).get()
            
            if data:
                return list(data.values())
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get activity for {collection}: {e}")
            return []
    
    def get_device_status(self, device: str = None) -> Dict[str, Any]:
        """Get device status from Firebase"""
        try:
            if not self.is_connected():
                return {}
            
            device_status_ref = self.database.child('device_status')
            
            if device:
                # Get specific device status
                status = device_status_ref.child(device).get()
                return status if status else {}
            else:
                # Get all device statuses
                all_status = device_status_ref.get()
                return all_status if all_status else {}
                
        except Exception as e:
            logger.error(f"Failed to get device status: {e}")
            return {}
    
    def update_system_status(self, status_data: Dict[str, Any]) -> bool:
        """Update system status information"""
        try:
            if not self.is_connected():
                return False
            
            status_data['last_update'] = datetime.now().isoformat()
            
            system_status_ref = self.database.child('system_status')
            system_status_ref.set(status_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status from Firebase"""
        try:
            if not self.is_connected():
                return {}
            
            system_status_ref = self.database.child('system_status')
            status = system_status_ref.get()
            
            return status if status else {}
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {} 