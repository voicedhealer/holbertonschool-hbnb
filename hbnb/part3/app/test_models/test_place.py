import unittest
from app import create_app, db
from app.models.place import Place
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity

class TestPlace(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        # Création d'un utilisateur "propriétaire"
        self.owner = User(
            username="alice",
            password="hashed",  # Mets un hash réel si tu as une méthode
            _first_name="Alice",
            _last_name="Smith",
            _email="alice.smith@example.com"
        )
        db.session.add(self.owner)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_place_creation_and_relationships(self):
        # Création d'un lieu
        place = Place(
            title="Cozy Apartment",
            description="A nice place to stay",
            price=100,
            latitude=37.7749,
            longitude=-122.4194,
            owner=self.owner
        )
        db.session.add(place)
        db.session.commit()
        self.assertEqual(place.title, "Cozy Apartment")
        self.assertEqual(place.price, 100)
        self.assertEqual(place.owner.id, self.owner.id)

        # Ajout d'un équipement
        wifi = Amenity(name="Wi-Fi")
        db.session.add(wifi)
        db.session.commit()
        place.amenities.append(wifi)
        db.session.commit()
        self.assertIn(wifi, place.amenities)

        # Ajout d'un avis
        review = Review(text="Super séjour", rating=5, place=place, user=self.owner)
        db.session.add(review)
        db.session.commit()
        self.assertIn(review, place.reviews)
        self.assertEqual(review.text, "Super séjour")

if __name__ == "__main__":
    unittest.main()
