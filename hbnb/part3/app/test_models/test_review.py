import unittest
from app import create_app, db
from app.models.review import Review

class TestReview(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_review_creation(self):
        review = Review(text="Super séjour", rating=5, place_id=1, user_id=1)
        db.session.add(review)
        db.session.commit()
        self.assertIsNotNone(review.id)
        self.assertEqual(review.text, "Super séjour")
        self.assertEqual(review.rating, 5)

    def test_review_text_required(self):
        with self.assertRaises(Exception):
            review = Review(text=None, rating=5, place_id=1, user_id=1)
            db.session.add(review)
            db.session.commit()
        db.session.rollback()

    def test_review_rating_required(self):
        with self.assertRaises(Exception):
            review = Review(text="Super séjour", rating=None, place_id=1, user_id=1)
            db.session.add(review)
            db.session.commit()
        db.session.rollback()

    def test_to_dict(self):
        review = Review(text="Parfait", rating=5, place_id=1, user_id=1)
        db.session.add(review)
        db.session.commit()
        self.assertEqual(
            review.to_dict(),
            {
                'id': review.id,
                'text': "Parfait",
                'rating': 5,
                'place_id': 1,
                'user_id': 1
            }
        )

if __name__ == "__main__":
    unittest.main()
