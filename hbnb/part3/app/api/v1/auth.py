from flask_restx import Namespace, Resource, fields
from flask import request, jsonify, Blueprint
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from functools import wraps
from app.services import facade

# Déclaration du Blueprint Flask pour l'auth
auth_bp = Blueprint('auth', __name__)

# Namespace RESTX pour la documentation et la structure d'API
api = Namespace('auth', description='Authentication operations')

# Modèle de validation des entrées pour Swagger/RESTX
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

# Décorateur pour restreindre l'accès selon le rôle
def role_required(role):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            if not current_user.get(role, False):
                return jsonify(msg=f"Accès refusé : {role} requis"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Endpoint Flask classique pour login (utile pour compatibilité ou tests)
@auth_bp.route('/login', methods=['POST'])
def login_flask():
    email = request.json.get('email')
    password = request.json.get('password')
    user = facade.get_user_by_email(email)
    if not user or not user.verify_password(password):
        return jsonify(msg="Identifiants invalides"), 401
    access_token = create_access_token(
        identity={'id': str(user.id), 'is_admin': user.is_admin}
    )
    return jsonify(access_token=access_token), 200

# Endpoint RESTX pour login (pour la doc et la structure d'API)
@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authentifier l'utilisateur et renvoyer un jeton JWT"""
        credentials = api.payload
        user = facade.get_user_by_email(credentials['email'])
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401
        access_token = create_access_token(
            identity={'id': str(user.id), 'is_admin': user.is_admin}
        )
        return {'access_token': access_token}, 200

# Exemple d'endpoint protégé, accessible à tout utilisateur connecté
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected_flask():
    current_user = get_jwt_identity()
    return jsonify(message=f'Hello, user {current_user["id"]}'), 200

# Exemple d'endpoint protégé RESTX
@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'message': f'Hello, user {current_user["id"]}'}, 200

# Exemple d'endpoint admin-only avec Blueprint Flask
@auth_bp.route('/admin-protected', methods=['GET'])
@role_required('is_admin')
def admin_protected_flask():
    current_user = get_jwt_identity()
    return jsonify(message=f'Bienvenue, admin {current_user["id"]}!'), 200

# Exemple d'endpoint admin-only RESTX
@api.route('/admin-protected')
class AdminProtectedResource(Resource):
    @role_required('is_admin')
    def get(self):
        current_user = get_jwt_identity()
        return {'message': f'Bienvenue, admin {current_user["id"]}!'}, 200
