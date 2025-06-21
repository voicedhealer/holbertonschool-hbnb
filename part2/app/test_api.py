import unittest
from app import create_app

class TestUserEndpoints(unittest.TestCase):

    def setUp(self):
        # Cette méthode sera appelée avant chaque test
        from app.services.facade import HBnBFacade
        self.facade = HBnBFacade()
        self.facade.user_repo._storage.clear()  # Vide le repo à chaque test
        self.app = create_app()
        self.client = self.app.test_client()
        # Appelle la route de reset pour vider le repo utilisé par l'API Flask
        self.client.post('/api/v1/users/_reset')

    def test_create_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)

    def test_create_user_with_existing_email(self):
        # Crée un utilisateur valide
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 201)

        # Tente de créer à nouveau avec le même email
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_create_user_invalid_data(self):
        # Email manquant -> doit échouer
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit"
            # pas d'email
        })
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 201)
        user_id = response.get_json()['id']

        response = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(response.status_code, 201)
        self.assertIn('Roger', response.get_data(as_text=True))

    def test_get_user_not_found(self):
        response = self.client.get('/api/v1/users/999')
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 201)
        user_id = response.get_json()['id']

        response = self.client.put(f'/api/v1/users/{user_id}', json={
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("Updated", response.get_data(as_text=True))

    def test_update_user_not_found(self):
        response = self.client.put('/api/v1/users/999', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()