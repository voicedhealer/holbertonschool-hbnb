import unittest
from app import create_app, db
from app.models.amenity import Amenity

class TestAmenity(unittest.TestCase):
    def setUp(self):
        # Crée une instance de l'application et pousse le contexte
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_amenity_creation(self):
        amenity = Amenity(name="Wi-Fi")
        db.session.add(amenity)
        db.session.commit()
        self.assertIsNotNone(amenity.id)
        self.assertEqual(amenity.name, "Wi-Fi")

    def test_amenity_name_required(self):
        with self.assertRaises(TypeError):
            Amenity()
        with self.assertRaises(ValueError):
            Amenity(name=None)
        with self.assertRaises(ValueError):
            Amenity(name="")

    def test_amenity_name_max_length(self):
        long_name = "a" * 51
        with self.assertRaises(ValueError):
            Amenity(name=long_name)

    def test_to_dict(self):
        amenity = Amenity(name="Piscine")
        db.session.add(amenity)
        db.session.commit()
        self.assertEqual(amenity.to_dict(), {'id': amenity.id, 'name': "Piscine"})

if __name__ == "__main__":
    unittest.main()
