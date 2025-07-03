from app import db
import uuid
from datetime import datetime, timezone

class BaseModel(db.Model):
    __abstract__ = True  # 🔥 Très important : cette classe ne crée pas de table seule

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def save(self):
        """Mettre à jour manuellement l'horodatage updated_at"""
        self.updated_at = datetime.now(timezone.utc)

    def update(self, data):
        """Met à jour les attributs de l'instance"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def is_max_length(self, name, value, max_length):
        if len(value) > max_length:
            raise ValueError(f"{name} must be {max_length} characters max.")

    def is_between(self, name, value, min_val, max_val):
        if not min_val < value < max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}.")

