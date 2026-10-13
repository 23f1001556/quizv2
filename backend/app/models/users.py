from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from app.configs.extensions import db
import re

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(30), unique=True, nullable=False)  # max 30 chars
    email = db.Column(db.String(50), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)
    fullname = db.Column(db.String(80))
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    isadmin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    # Relationships
    scores = db.relationship("Scores", back_populates="user", cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError("Password is write-only")

    @password.setter
    def password(self, value):
        # Validate password strength
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).{6,}$', value):
            raise ValueError("Password must contain uppercase, lowercase, number, special char and min 6 chars")
        self._password = generate_password_hash(value)

    def check_password(self, value):
        return check_password_hash(self._password, value)

    @staticmethod
    def format_username(username):
        return username.upper()

    @staticmethod
    def format_email(email):
        return email.lower()

    def get_token(self, salt='email-confirm', expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=salt)

    @staticmethod
    def generate_registration_token(data, salt='email-confirm', expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps(data, salt=salt)

    @staticmethod
    def verify_registration_token(token, salt='email-confirm'):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt=salt, max_age=1800)
            return data
        except:
            return None

    @staticmethod
    def verify_token(token, salt='email-confirm'):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt=salt, max_age=1800)['user_id']
        except:
            return None
        return User.query.get(user_id)
