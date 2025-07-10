import uuid
from app.extensions import db
from app.models.base_model import BaseModel

class Place(BaseModel, db.Model):
    __tablename__ = 'places'
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(60), db.ForeignKey('users.id'), nullable=False)

    # Relations
    reviews = db.relationship('Review', back_populates='place', cascade="all, delete-orphan")
    amenities = db.relationship('PlaceAmenity', back_populates='place', cascade="all, delete-orphan")

    @staticmethod
    def validate_data(data):
        if not data.get('title') or len(data['title']) > 100:
            raise ValueError("Title is required and must be <= 100 chars")
        if 'price' not in data or float(data['price']) <= 0:
            raise ValueError("Price must be positive")
        if 'latitude' not in data or not (-90.0 <= float(data['latitude']) <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0")
        if 'longitude' not in data or not (-180.0 <= float(data['longitude']) <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0")
        if not data.get('owner_id'):
            raise ValueError("Owner (owner_id) is required")

class PlaceAmenity(db.Model):
    __tablename__ = 'place_amenity'
    place_id = db.Column(db.String(60), db.ForeignKey('places.id'), primary_key=True)
    amenity_id = db.Column(db.String(60), db.ForeignKey('amenities.id'), primary_key=True)
    place = db.relationship('Place', back_populates='amenities')
    amenity = db.relationship('Amenity', back_populates='places')