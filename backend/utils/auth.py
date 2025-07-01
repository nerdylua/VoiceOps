"""
Authentication utilities for VoiceOps Backend
Simple JWT-based authentication for API endpoints
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config.settings import Config

logger = logging.getLogger(__name__)

def generate_auth_token(username: str, user_type: str = 'admin') -> str:
    """Generate JWT authentication token"""
    try:
        payload = {
            'username': username,
            'user_type': user_type,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=Config.SESSION_TIMEOUT)
        }
        
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        logger.info(f"Generated auth token for user: {username} (type: {user_type})")
        return token
        
    except Exception as e:
        logger.error(f"Error generating auth token: {e}")
        return ""

def generate_jwt_token(user_id: str, username: str, user_type: str = 'user') -> str:
    """Generate JWT token for QR-based authentication"""
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'user_type': user_type,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=Config.SESSION_TIMEOUT)
        }
        
        token = jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
        logger.info(f"Generated JWT token for user: {username} (ID: {user_id})")
        return token
        
    except Exception as e:
        logger.error(f"Error generating JWT token: {e}")
        return ""

def validate_auth(token: str) -> bool:
    """Validate JWT authentication token"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        
        # Check if token has expired
        exp_time = datetime.fromtimestamp(payload['exp'])
        if datetime.utcnow() > exp_time:
            logger.warning("Token has expired")
            return False
        
        logger.debug(f"Token validated for user: {payload.get('username')}")
        return True
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return False
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return False
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        return False

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT token and return payload"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None 