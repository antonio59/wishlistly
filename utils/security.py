from functools import wraps
from flask import request, current_app
from datetime import datetime, timedelta
import jwt
from flask_login import current_user
from werkzeug.security import generate_password_hash
import time
from collections import defaultdict

# In-memory storage for rate limiting
rate_limit_storage = defaultdict(list)

def generate_reset_token(user_id):
    """Generate a JWT token for password reset"""
    expiration = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(
        {
            'reset_password': user_id,
            'exp': expiration
        },
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

def verify_reset_token(token):
    """Verify a password reset token"""
    try:
        data = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return data['reset_password']
    except:
        return None

def rate_limit(limit=5, window=60):
    """Rate limiting decorator using in-memory storage"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            # Create a unique key for this route and IP
            key = f"{client_ip}:{request.endpoint}"
            
            current_time = time.time()
            # Clean up old requests
            rate_limit_storage[key] = [t for t in rate_limit_storage[key] if current_time - t < window]
            
            # Check if limit is exceeded
            if len(rate_limit_storage[key]) >= limit:
                return {'error': 'Rate limit exceeded'}, 429
            
            # Add current request
            rate_limit_storage[key].append(current_time)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def update_password_hash(user, new_password):
    """Update user's password hash"""
    user.password_hash = generate_password_hash(new_password)
    return user

def require_2fa(f):
    """Decorator to require 2FA for sensitive operations"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'error': 'Authentication required'}, 401
        if not current_user.is_verified:
            return {'error': '2FA verification required'}, 403
        return f(*args, **kwargs)
    return decorated_function
