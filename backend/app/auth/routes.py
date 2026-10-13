from flask import Blueprint, jsonify, request, current_app, url_for
from app.models.users import User
from app.configs.extensions import db, blacklist, mail
from flask_mail import Message
from app.auth.decors import login_required
import re
import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError

from app.celery.tasks import send_reset_password_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Forgot Password
@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return jsonify({"message": "Email is required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            # For security, standard practice is to not reveal if user exists, 
            # but for this specific request context we mimic typical behavior. 
            # Or we can return 200 even if not found. Let's return 404 for clarity in dev.
            return jsonify({"message": "User not found"}), 404

        token = user.get_token(salt='password-reset')
        # Assuming Frontend runs on localhost:5173 
        # Ideally this URL should be in config
        frontend_url = "http://localhost:5173/reset-password" 
        reset_link = f"{frontend_url}/{token}"

        send_reset_password_email.delay(email, reset_link)

        return jsonify({"message": "Password reset link sent to email"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route("/reset_password/<token>", methods=["POST"])
def reset_password(token):
    try:
        data = request.get_json()
        new_password = data.get("password")

        if not new_password:
             return jsonify({"message": "Password is required"}), 400

        user = User.verify_token(token, salt='password-reset')
        if not user:
            return jsonify({"message": "Invalid or expired token"}), 400

        user.password = new_password
        db.session.commit()

        return jsonify({"message": "Password reset successfully"}), 200

    except ValueError as val:
        return jsonify({"message": str(val)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Helper function
def get_token_from_header():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None, "Authorization header missing"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None, "Authorization header must be Bearer token"
    return parts[1], None


# Login
@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = User.format_email(data.get("email"))
        password = data.get("password")

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        if not user.check_password(password):
            return jsonify({"message": "Invalid password"}), 401

        if not user.is_verified:
            return jsonify({"message": "Please verify your email before logging in."}), 403

        if hasattr(user, 'is_blocked') and user.is_blocked:
            return jsonify({"message": "Your account has been blocked. Please contact support."}), 403

        token = jwt.encode({
            "user_id": user.id,
            "isadmin": user.isadmin,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, current_app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.user_name,
                "email": user.email,
                "isadmin": user.isadmin
            }
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Register
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        username = User.format_username(data.get("username"))
        email = User.format_email(data.get("email"))
        password = data.get("password")

        if len(username) < 5 or len(username) > 20:
            return jsonify({"message": "username must be 5-20 characters"}), 400
        if len(password) < 8:
            return jsonify({"message": "password too short"}), 400

        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).{8,}$'
        if not re.match(pattern, password):
            return jsonify({"message": "Password must be 8+ chars, include uppercase, lowercase, number & special char"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"message": "This Email Is Already Registered"}), 400
        if User.query.filter_by(user_name=username).first():
            return jsonify({"message": "This Username Is Already Taken"}), 400

        # Create a temporary user to get the hashed password
        temp_user = User(user_name=username, email=email)
        temp_user.password = password
        hashed_password = temp_user._password

        # Generate registration token with data
        reg_data = {
            "username": username,
            "email": email,
            "password": hashed_password
        }
        token = User.generate_registration_token(reg_data)

        frontend_url = "http://localhost:5173/verify-email"
        verify_link = f"{frontend_url}/{token}"

        try:
            msg = Message(
                subject="Verify your email",
                recipients=[email],
                body=f"Click this link to verify your email:\n{verify_link}"
            )
            mail.send(msg)
            return jsonify({"message": f"Verification email sent to {email}. Please check your inbox."}), 201
        except Exception as email_error:
            print(f"Email sending failed: {email_error}")
            return jsonify({"message": f"Failed to send verification email. Please contact support."}), 500

    except ValueError as val:
        return jsonify({"message": str(val)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@auth_bp.route("/verify_email/<token>", methods=["GET"])
def verify_email(token):
    try:
        data = User.verify_registration_token(token)
        if not data:
             # Check if it was a legacy token (user_id based) or just invalid
             return jsonify({"message": "Invalid or expired token", "status": "error"}), 400
        
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        if User.query.filter_by(email=email).first():
             return jsonify({"message": "User already verified and registered", "status": "success"}), 200

        user = User(user_name=username, email=email)
        user._password = password
        user.is_verified = True
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"message": "Email verified and account created successfully", "status": "success"}), 200
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500


# Logout
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    try:
        token, error = get_token_from_header()
        if error:
            return jsonify({"message": error}), 401

        blacklist.add(token)
        return jsonify({"message": "Logout successful"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# Current user info
@auth_bp.route("/getme", methods=["GET"])
@login_required
def current_user():
    try:
        token, error = get_token_from_header()
        if error:
            return jsonify({"message": error}), 401

        if token in blacklist:
            return jsonify({"message": "Token has been revoked"}), 401

        try:
            payload = jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except ExpiredSignatureError:
            return jsonify({"message": "Token expired"}), 401
        except InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        user = User.query.filter_by(id=payload["user_id"]).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify({
            "message": "User found",
            "user": {
                "username": user.user_name,
                "email": user.email,
                "isadmin": user.isadmin
            }
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@auth_bp.route("/verify_password", methods=["POST"])
@login_required
def verify_password():
    try:
        data = request.get_json()
        password = data.get("password")
        if not password:
            return jsonify({"message": "Password is required"}), 400

        user = User.query.get(request.user_id)
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid password", "verified": False}), 401

        return jsonify({"message": "Password verified", "verified": True}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
