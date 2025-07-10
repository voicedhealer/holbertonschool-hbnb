from app.extensions import db
from app.models.review import Review

class ReviewRepository:
    @staticmethod
    def get(review_id):
        return db.session.get(Review, review_id)

    @staticmethod
    def get_all():
        return Review.query.all()

    @staticmethod
    def get_by_place(place_id):
        return Review.query.filter_by(place_id=place_id).all()

    @staticmethod
    def create(review):
        db.session.add(review)
        db.session.commit()
        return review

    @staticmethod
    def update(review):
        db.session.commit()
        return review

    @staticmethod
    def delete(review):
        db.session.delete(review)
        db.session.commit()
