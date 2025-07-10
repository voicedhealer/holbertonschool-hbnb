from app.extensions import db
from app.models.amenity import Amenity

class AmenityRepository:
    @staticmethod
    def get(amenity_id):
        return db.session.get(Amenity, amenity_id)

    @staticmethod
    def get_all():
        return Amenity.query.all()

    @staticmethod
    def create(amenity):
        db.session.add(amenity)
        db.session.commit()
        return amenity

    @staticmethod
    def update(amenity):
        db.session.commit()
        return amenity

    @staticmethod
    def delete(amenity):
        db.session.delete(amenity)
        db.session.commit()
