from flask import Blueprint, request, jsonify
from app.models.user import User

users_bp = Blueprint('users', __name__)

# Stockage temporaire (à remplacer par la base de données ou repository)
users = {}

@users_bp.route('/api/v1/users/', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(**data)
    users[user.id] = user
    return jsonify({"id": user.id}), 201

@users_bp.route('/api/v1/users/', methods=['GET'])
def list_users():
    return jsonify([user.__dict__ for user in users.values()]), 200

@users_bp.route('/api/v1/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.__dict__), 200

@users_bp.route('/api/v1/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    user.update(**data)
    return jsonify(user.__dict__), 200
