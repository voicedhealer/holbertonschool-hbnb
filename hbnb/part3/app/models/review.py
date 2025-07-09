from .basemodel import BaseModel
from .place import Place
from .user import User
from app import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.Integer, db.ForeignKey('places.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('app_users.id'), nullable=False)

    # Relations (optionnelles mais recommandées)
    place = db.relationship('Place', backref='reviews')
    user = db.relationship('User', backref='reviews')

def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'rating': self.rating,
            'place_id': self.place_id,
            'user_id': self.user_id
        }

def __repr__(self):
        return f'<Review {self.id} - {self.rating}/5>'
