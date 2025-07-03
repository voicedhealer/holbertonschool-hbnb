from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

api = Namespace('auth', description='Authentication operations')
auth_bp = Blueprint('auth', __name__)

# Modèle de validation des entrées
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

def role_required(role):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if not claims.get(role, False):
                return jsonify(msg=f"Accès refusé : {role} requis"), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    # Remplace cette logique par la tienne (vérification en base)
    if username == 'admin' and password == 'adminpass':
        access_token = create_access_token(identity=username, additional_claims={"is_admin": True})
        return jsonify(access_token=access_token)
    elif username == 'user' and password == 'userpass':
        access_token = create_access_token(identity=username, additional_claims={"is_admin": False})
        return jsonify(access_token=access_token)
    return jsonify(msg="Identifiants invalides"), 401

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authentifier l'utilisateur et renvoyer un jeton JWT"""
        credentials = api.payload  # Récupérez l'e-mail et le mot de passe à partir de la charge utile de la requête
        
        # Étape 1 : Récupérer l'utilisateur en fonction de l'e-mail fourni
        user = facade.get_user_by_email(credentials['email'])
        
        # Étape 2 : Vérifiez si l’utilisateur existe et si le mot de passe est correct
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Étape 3 : Créez un jeton JWT avec l'ID de l'utilisateur et l'indicateur is_admin
        access_token = create_access_token(identity={'id': str(user.id), 'is_admin': user.is_admin})
        
        # Étape 4 : renvoyer le jeton JWT au client
        return {'access_token': access_token}, 200

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        """Un point de terminaison protégé qui nécessite un jeton JWT valide"""
        current_user = get_jwt_identity()  # Récupérer l'identité de l'utilisateur à partir du jeton
        return {'message': f'Hello, user {current_user["id"]}'}, 200
    