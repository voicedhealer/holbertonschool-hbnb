# test_app.py
import sys
import os
import pytest
from part2.app.models.user import User

def test_create_user():
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com", password="securepassword", is_admin=False)
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"