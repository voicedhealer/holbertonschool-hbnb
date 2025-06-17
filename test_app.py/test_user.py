# test_app.py
import sys
import os
import pytest
from part2.app.models.user import User

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code in (200, 404)  # selon si tu as une route /

def test_create_user(client):
    response = client.post(
        "/api/v1/users/",
        json={"first_name": "John", "last_name": "Doe", "email": "john.doe@example.com"}
    )
    assert response.status_code in (200, 201)
    data = response.get_json()
    assert data["first_name"] == "John"