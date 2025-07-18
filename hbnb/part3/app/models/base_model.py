import uuid
from datetime import datetime
from app.extensions import db  # ou `from app import db` selon ton architecture

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def save(self):
        """Enregistre l'objet dans la base de données."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Supprime l'objet de la base de données."""
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        """Convertit l'objet en dictionnaire simple (utile pour les APIs ou jsonify)."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
