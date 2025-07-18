import uuid
from app.extensions import db
from app.models.base_model import BaseModel

class Amenity(BaseModel, db.Model):
    __tablename__ = 'amenities'

    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False, unique=True)

    # Relation vers PlaceAmenity
    places = db.relationship(
        'PlaceAmenity',
        back_populates='amenity',
        cascade="all, delete-orphan",
        lazy="select"
    )

    @staticmethod
    def validate_data(data):
        if not data.get('name') or len(data['name']) > 50:
            raise ValueError("Amenity name is required and must be <= 50 chars")

    def __repr__(self):
        return f"<Amenity {self.name}>"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Amenity.validate_data(kwargs)
