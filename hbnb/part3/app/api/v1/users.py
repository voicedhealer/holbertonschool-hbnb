from flask_restx import Namespace, Resource, fields
from flask import request
from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask import abort
from app.services import facade
from app.models.user import User
from .auth import role_required

users_bp = Blueprint('users', __name__)
api = Namespace('users', description='User operations')
login_model = api.model('Login', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})
# Défini le modèle utilisateur pour la validation et la documentation des entrées
user_model = api.model('User', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'is_admin': fields.Boolean()  # création d’un user admin via l’API
})

@users_bp.route('/admin2', methods=['GET'])
@role_required('is_admin')
def admin_only2():
    return jsonify(msg="Bienvenue, administrateur (version décorateur) !"), 200

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def user_profile():
    return jsonify(msg="Profil utilisateur accessible !"), 200

@users_bp.route('/admin', methods=['GET'])
@jwt_required()
def admin_only():
    claims = get_jwt()
    if not claims.get('is_admin', False):
        return jsonify(msg="Accès refusé : administrateur requis"), 403
    return jsonify(msg="Bienvenue, administrateur !"), 200

# --- Endpoints réservés aux admins ---

@api.route('/')
class AdminUserCreateList(Resource):
    @api.expect(user_model, validate=True)
    @jwt_required()
    def post(self):
        """Créer un nouvel utilisateur (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload or request.json
        email = user_data.get('email')
        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400
        try:
            new_user = facade.create_user(user_data)
            return {'id': new_user.id, 'message': 'User successfully created'}, 201
        except Exception as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of users retrieved successfully')
    @jwt_required()
    def get(self):
        """Lister tous les utilisateurs (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403
        users = facade.get_users()
        return [user.to_dict() for user in users], 200

@api.route('/<user_id>')
class AdminUserResource(Resource):
    @api.response(200, 'User details retrieved successfully')
    @api.response(404, 'User not found')
    @jwt_required()
    def get(self, user_id):
        """Obtenir les détails d'un utilisateur par ID (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403
        user = facade.get_user_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict(), 200

    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def put(self, user_id):
        """Mettre à jour un utilisateur (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403

        user_data = api.payload or request.json
        user = facade.get_user_by_id(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        email = user_data.get('email')
        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and str(existing_user.id) != str(user_id):
                return {'error': 'Email already in use'}, 400

        try:
            updated_user = facade.update_user(user_id, user_data)
            return updated_user.to_dict(), 200
        except Exception as e:
            return {'error': str(e)}, 400

# --- Endpoints accessibles à l'utilisateur connecté ---

@api.route('/me')
class Me(Resource):
    @jwt_required()
    def get(self):
        """Obtenir les infos de l'utilisateur connecté"""
        user_id = get_jwt_identity()
        claims = get_jwt()
        user = User.query.get(user_id)
        return {
            "username": user.username,
            "is_admin": claims.get("is_admin", False)
        }

# --- Endpoint de connexion ---

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Connexion utilisateur et récupération du token JWT"""
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.verify_password(data['password']):
            additional_claims = {"is_admin": user.is_admin}
            token = create_access_token(identity=user.id, additional_claims=additional_claims)
            return {"access_token": token}, 200
        return {"msg": "Mauvais identifiants"}, 401

# --- Endpoint bonus pour tester l'accès admin ---

@api.route('/admin')
class AdminOnly(Resource):
    @jwt_required()
    def get(self):
        """Endpoint protégé accessible uniquement aux administrateurs"""
        claims = get_jwt()
        if not claims.get("is_admin", False):
            return {'error': 'Admin privileges required'}, 403
        return {"msg": "Bienvenue, admin !"}
