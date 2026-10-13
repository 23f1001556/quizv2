from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.configs.extensions import blacklist

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token missing"}), 401
        try:
            # Expecting token as "Bearer <token>"
            if " " in token:
                token = token.split()[1]
            
            if token in blacklist:
                return jsonify({"message": "Token has been revoked"}), 401

            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            # Attach user info to request
            user_id = payload["user_id"]
            
            # Check if user is blocked
            from app.models.users import User
            user = User.query.get(user_id)
            if not user:
                return jsonify({"message": "User not found"}), 404
            if hasattr(user, 'is_blocked') and user.is_blocked:
                return jsonify({"message": "Your account has been blocked. Please contact support."}), 403

            request.user_id = user_id
            # Default isadmin to False if not present (for backward compatibility with old tokens)
            request.isadmin = payload.get("isadmin", False)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        except Exception as e:
            return jsonify({"message": str(e)}), 401
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @login_required 
    def decorated(*args, **kwargs):
        if not getattr(request, "isadmin", False):
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

def protect_super_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        target_id = kwargs.get("id")
        if target_id is not None:
            from app.models.users import User
            target_user = User.query.get(target_id)
            if target_user and target_user.isadmin:
                return jsonify({"message": "Action not allowed on administrator accounts"}), 403
        return f(*args, **kwargs)
    return decorated
