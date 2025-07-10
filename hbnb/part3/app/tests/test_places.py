import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from app import create_app, db
from app.models.user import User
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
            # Création d'une amenity seulement
            amenity = Amenity(name='Wifi')
            db.session.add(amenity)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()

def get_auth_token(client):
    resp = client.post('/api/v1/users/', json={
        'first_name': 'Alice',
        'last_name': 'Doe',
        'email': 'alice@example.com',
        'password': 'password'
    })
    print("USER CREATION STATUS:", resp.status_code)
    print("USER CREATION RESPONSE:", resp.get_json())
    assert resp.status_code in (200, 201), f"Erreur création user : {resp.data!r}"

    resp = client.post('/api/v1/auth/login', json={
        'email': 'alice@example.com',
        'password': 'password'
    })
    print("LOGIN STATUS:", resp.status_code)
    print("LOGIN RESPONSE:", resp.get_json())
    data = resp.get_json()
    assert data is not None, f"Pas de JSON dans la réponse login : {resp.data!r} (status {resp.status_code})"
    assert 'access_token' in data, f"Pas de access_token dans la réponse login : {data}"
    return data['access_token']

def test_create_place(client):
    token = get_auth_token(client)
    # Récupère l'id du user et de l'amenity
    with client.application.app_context():
        user = User.query.filter_by(email='alice@example.com').first()
        amenity = Amenity.query.filter_by(name='Wifi').first()
        owner_id = user.id
        amenity_id = amenity.id

    payload = {
        'title': 'Super appart',
        'description': 'Très bien situé',
        'price': 120.0,
        'latitude': 48.8566,
        'longitude': 2.3522,
        'owner_id': owner_id,
        'amenities': [amenity_id]
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = client.post('/api/v1/places/', json=payload, headers=headers)
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.get_json())
    assert resp.status_code == 201, f"Attendu 201, reçu {resp.status_code} : {resp.data!r}"
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse : {resp.data!r}"
    assert data.get('title') == 'Super appart'
    assert data.get('owner_id') == owner_id

def test_get_places(client):
    resp = client.get('/api/v1/places/')
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.get_json())
    assert resp.status_code == 200, f"Attendu 200, reçu {resp.status_code} : {resp.data!r}"
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse : {resp.data!r}"

def test_create_place_missing_field(client):
    token = get_auth_token(client)
    headers = {'Authorization': f'Bearer {token}'}
    payload = {
        'title': 'Sans prix',
        # 'price' manquant
        'latitude': 48.0,
        'longitude': 2.0,
        'owner_id': 'dummy',
        'amenities': []
    }
    resp = client.post('/api/v1/places/', json=payload, headers=headers)
    print("STATUS CODE:", resp.status_code)
    print("RESPONSE JSON:", resp.get_json())
    assert resp.status_code == 400, f"Attendu 400, reçu {resp.status_code} : {resp.data!r}"
    try:
        data = resp.get_json()
    except Exception:
        data = None
    assert data is not None, f"Pas de JSON dans la réponse : {resp.data!r}"
    assert "error" in data or "errors" in data, f"Pas de clé 'error' ou 'errors' dans la réponse : {data}"
