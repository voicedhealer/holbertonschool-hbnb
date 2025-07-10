from app.extensions import db
from app.models.place import Place

class PlaceRepository:
    @staticmethod
    def get(place_id):
        return db.session.get(Place, place_id)

    @staticmethod
    def get_all():
        return Place.query.all()

    @staticmethod
    def create(place):
        db.session.add(place)
        db.session.commit()
        return place

    @staticmethod
    def update(place):
        db.session.commit()
        return place

    @staticmethod
    def delete(place):
        db.session.delete(place)
        db.session.commit()
