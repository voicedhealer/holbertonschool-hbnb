import uuid
import re
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel

class User(BaseModel, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    places = db.relationship('Place', backref='owner', lazy=True)
    reviews = db.relationship('Review', back_populates='user', cascade="all, delete-orphan")

    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_data(data):
        if not data.get('first_name') or len(data['first_name']) > 50:
            raise ValueError("first_name is required and must be <= 50 chars")
        if not data.get('last_name') or len(data['last_name']) > 50:
            raise ValueError("last_name is required and must be <= 50 chars")
        if not data.get('email') or not User.EMAIL_REGEX.match(data['email']):
            raise ValueError("Valid email is required")
        if not data.get('password') or len(data['password']) < 6:
            raise ValueError("Password is required and must be >= 6 chars")
