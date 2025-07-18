import uuid
import re
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base_model import BaseModel

class User(BaseModel, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    places = db.relationship('Place', backref='owner', lazy='select', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='user', lazy='select', cascade="all, delete-orphan")

    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    # SUPPRIME : pas de validation dans __init__
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Ne jamais exposer le mot de passe."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def validate_data(data):
        if not data.get('first_name') or len(data['first_name']) > 50:
            raise ValueError("First name is required and must be <= 50 chars")
        if not data.get('last_name') or len(data['last_name']) > 50:
            raise ValueError("Last name is required and must be <= 50 chars")
        if not data.get('email') or not User.EMAIL_REGEX.match(data['email']):
            raise ValueError("Valid email is required")
        if not data.get('password') or len(data['password']) < 6:
            raise ValueError("Password is required and must be >= 6 characters")

    def __repr__(self):
        return f"<User {self.id} - {self.email}>"
