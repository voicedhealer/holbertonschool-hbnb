import unittest
from sqlalchemy.exc import IntegrityError
from app import create_app, db
from app.models.user import User

class TestUser(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        user = User(
            username="johndoe",
            password="MySecret123",  # Si tu veux stocker le hash, fais user.hash_password(...)
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        db.session.add(user)
        db.session.commit()
        self.assertEqual(user.username, "johndoe")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.email, "john.doe@example.com")
        self.assertFalse(user.is_admin)
        expected = {
            'id': user.id,
            'username': "johndoe",
            'first_name': "John",
            'last_name': "Doe",
            'email': "john.doe@example.com",
            'is_admin': False,
            'role': 'user'  # adapte selon ta méthode to_dict
        }
        for key in expected:
            self.assertEqual(user.to_dict()[key], expected[key])

    def test_user_max_length(self):
        with self.assertRaises(ValueError):
            User(
                username="johndoe",
                password="MySecret123",
                first_name="a" * 51,
                last_name="Doe",
                email="john.doe@example.com"
            )
        with self.assertRaises(ValueError):
            User(
                username="johndoe",
                password="MySecret123",
                first_name="John",
                last_name="a" * 51,
                email="john.doe@example.com"
            )

    def test_user_email(self):
        with self.assertRaises(ValueError):
            User(
                username="johndoe",
                password="MySecret123",
                first_name="John",
                last_name="Doe",
                email="john.doeexample.com"
            )

    def test_user_required_fields(self):
        user = User(
            username="johndoe",
            password="MySecret123",
            first_name="John",
            last_name="Doe"
            # email manquant
        )
        db.session.add(user)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_user_update(self):
        user = User(
            username="johndoe",
            password="MySecret123",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        new_data = {
            'first_name': "Jane",
            'last_name': "Dupont",
            'email': "jane.dupont@example.com"
        }
        user.update(new_data)
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.last_name, "Dupont")
        self.assertEqual(user.email, "jane.dupont@example.com")

    def test_user_update_fail(self):
        user = User(
            username="johndoe",
            password="MySecret123",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        with self.assertRaises(ValueError):
            user.first_name = "a" * 51
        with self.assertRaises(ValueError):
            user.last_name = "a" * 51
        with self.assertRaises(ValueError):
            user.email = "john.doeexample.com"

    def test_user_password_hash_and_verify(self):
        user = User(
            username="johndoe",
            password="MySecret123",
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com"
        )
        user.hash_password("MySecret123")
        self.assertTrue(user.verify_password("MySecret123"))
        self.assertFalse(user.verify_password("WrongPassword"))

if __name__ == "__main__":
    unittest.main()
