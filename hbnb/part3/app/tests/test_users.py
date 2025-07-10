import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_user(client):
    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'password': 'secret'
    }
    response = client.post('/api/v1/users/', json=data)    
    print("RESPONSE JSON:", response.json)
    assert response.status_code == 201
    assert b'john@example.com' in response.data
