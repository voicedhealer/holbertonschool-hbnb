import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity

@pytest.fixture
def client():
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Création d'une amenity
            amenity = Amenity(name='Wifi')
            db.session.add(amenity)
            db.session.commit()
            # Création d'un utilisateur pour owner
            user = User(first_name='Bob', last_name='Smith', email='bob@example.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
            # Création d'un place
            place = Place(
                title="Test Place",
                description="Test desc",
                price=100.0,
                latitude=0.0,
                longitude=0.0,
                owner_id=user.id
            )
            db.session.add(place)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def get_auth_token(client):
    # Création de l'utilisateur (si déjà existant, ce n'est pas grave)
    client.post('/api/v1/users/', json={
        'first_name': 'Bob',
        'last_name': 'Smith',
        'email': 'bob@example.com',
        'password': 'password'
    })
    resp = client.post('/api/v1/auth/login', json={
        'email': 'bob@example.com',
        'password': 'password'
    })
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse login : {resp.data!r} (status {resp.status_code})"
    assert 'access_token' in data, f"Pas de access_token dans la réponse login : {data}"
    return data['access_token']

def test_create_review(client):
    token = get_auth_token(client)
    with client.application.app_context():
        user = User.query.filter_by(email='bob@example.com').first()
        place = Place.query.first()
        user_id = user.id
        place_id = place.id

    payload = {
        'text': 'Super séjour !',
        'rating': 5,
        'user_id': user_id,
        'place_id': place_id
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/reviews/', json=payload, headers=headers)
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.get_json())
    assert resp.status_code == 201, f"Attendu 201, reçu {resp.status_code} : {resp.data!r}"
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse : {resp.data!r}"
    assert data.get('text') == 'Super séjour !'
    assert data.get('user_id') == user_id

def test_get_reviews(client):
    resp = client.get('/api/v1/reviews/')
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.get_json())
    assert resp.status_code == 200, f"Attendu 200, reçu {resp.status_code} : {resp.data!r}"
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse : {resp.data!r}"

def test_create_review_invalid_rating(client):
    token = get_auth_token(client)
    with client.application.app_context():
        user = User.query.filter_by(email='bob@example.com').first()
        place = Place.query.first()
        user_id = user.id
        place_id = place.id

    payload = {
        'text': 'Bof',
        'rating': 10,  # Note invalide
        'user_id': user_id,
        'place_id': place_id
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/reviews/', json=payload, headers=headers)
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.get_json())
    assert resp.status_code == 400, f"Attendu 400, reçu {resp.status_code} : {resp.data!r}"
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse : {resp.data!r}"
    assert "error" in data, f"Pas de clé 'error' dans la réponse : {data}"
