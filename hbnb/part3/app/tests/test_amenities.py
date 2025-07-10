import pytest
from app import create_app, db

@pytest.fixture
def client():
    app = create_app('testing')  # Assure-toi d'avoir une config 'testing'
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_amenity(client):
    # Suppose que l’auth n’est pas obligatoire pour GET
    response = client.post('/api/v1/amenities/', json={'name': 'Wifi'})
    assert response.status_code == 401  # JWT requis

def test_get_amenities(client):
    # Ajoute une amenity pour le test
    from app.models.amenity import Amenity
    from app import db
    with client.application.app_context():
        db.session.add(Amenity(name='Wifi'))
        db.session.commit()
    response = client.get('/api/v1/amenities/')
    print("RESPONSE JSON:", response.json)
    assert response.status_code == 200
    assert b'Wifi' in response.data
