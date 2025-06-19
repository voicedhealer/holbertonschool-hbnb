import unittest
from app import create_app

class TestUserEndpoints(unittest.TestCase):

    def setUp(self):
        from app.services.facade import HBnBFacade
        self.facade = HBnBFacade()
        self.facade.user_repo._storage.clear()  # Vide le repo à chaque test
        self.app = create_app()
        self.client = self.app.test_client()

    def test_create_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 201)

    def test_create_user_invalid_data(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "",
            "last_name": "",
            "email": "invalid-email"
        })
        self.assertEqual(response.status_code, 400)

    def test_get_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        user_id = response.get_json()['id']

        response = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(response.status_code, 200)
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
        user_id = response.get_json()['id']

        response = self.client.put(f'/api/v1/users/{user_id}', json={
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("Updated", response.get_data(as_text=True))

    def test_update_user_not_found(self):
        response = self.client.put('/api/v1/users/999', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 404)

    def test_get_all_users(self):
        self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Roger', response.get_data(as_text=True))

    def test_get_all_users_empty(self):
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('[]', response.get_data(as_text=True))

    def test_create_user_with_existing_email(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 201)

        response = self.client.post('/api/v1/users/', json={
            "first_name": "Roger",
            "last_name": "Rabbit",
            "email": "roger.rabbit@example.com"
        })
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
