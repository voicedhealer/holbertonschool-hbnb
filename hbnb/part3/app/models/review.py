import uuid
from app.extensions import db
from app.models.base_model import BaseModel

class Review(BaseModel, db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Relations
    place = db.relationship('Place', back_populates='reviews', lazy="select")
    user = db.relationship('User', back_populates='reviews', lazy="select")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Review.validate_data(kwargs)

    @staticmethod
    def validate_data(data):
        if not data.get('text'):
            raise ValueError("Review text is required")
        if 'rating' not in data:
            raise ValueError("Rating is required")
        try:
            rating = int(data['rating'])
        except (ValueError, TypeError):
            raise ValueError("Rating must be an integer")
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        if not data.get('place_id'):
            raise ValueError("Place ID is required")
