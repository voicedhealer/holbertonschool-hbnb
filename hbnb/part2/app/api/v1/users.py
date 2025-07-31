from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask import abort
from app.services import facade
from app.models.user import User


api = Namespace('users', description='User operations')


# MODELES SWAGGER
user_register_model = api.model('Register', {
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name': fields.String(required=True, description='Nom'),
    'email': fields.String(required=True, description='Email'),
    'username': fields.String(required=True, description='Nom d\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe'),
    'role': fields.String(
        required=True,
        description="Rôle utilisateur ('owner' ou 'voyageur')",
        enum=['owner', 'voyageur']
    ),
})

user_model = api.model('User', {
    'id': fields.String(description='ID utilisateur'),
    'first_name': fields.String(description='Prénom'),
    'last_name': fields.String(description='Nom'),
    'email': fields.String(description='Email'),
    'username': fields.String(description='Nom d\'utilisateur'),
    'role': fields.String(description='Rôle (owner/voyageur)'),
    'profile_picture': fields.String(description='Photo de profil'),
    'is_admin': fields.Boolean(description='Administrateur')
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Nom d\'utilisateur ou email'),
    'password': fields.String(required=True, description='Mot de passe')
})

# --- ENDPOINT ADMIN ---
@api.route('/admin')
class AdminOnly(Resource):
    @api.doc(security='jwt')
    @jwt_required()
    def get(self):
        claims = get_jwt()
        if not claims.get("is_admin", False):
            abort(403, "Accès réservé aux administrateurs")
        return {"msg": "Bienvenue, admin !"}

# --- INFOS USER CONNECTE ---
@api.route('/me')
class Me(Resource):
    @api.doc(security='jwt')
    @jwt_required()
    @api.marshal_with(user_model)
    def get(self):
        """Récupération des informations de l'utilisateur connecté"""
        user_id = get_jwt_identity()
        user = facade.get_user(user_id)
        if not user:
            abort(404, "Utilisateur inconnu")
        return user_id.to_dict(), 200

# --- REGISTER : POST /api/v1/users/register ---
@api.route('/register')
class UserRegister(Resource):
    @api.expect(user_register_model, validate=True)
    @api.response(201, 'User successfully created', user_model)
    @api.response(400, 'Email or username already registered')
    @api.response(422, 'Validation error')
    def post(self):
        """
        Inscription d'un nouvel utilisateur (propriétaire ou voyageur)
        """
        user_data = api.payload

        # ✅ DEBUG COMPLET pour traquer les problèmes
        print(f"=== DEBUG INSCRIPTION SERVEUR ===")
        print(f"Données reçues: {user_data}")
        print(f"Username: {user_data.get('username')}")
        print(f"Role: {user_data.get('role')}")
        print(f"Type du rôle: {type(user_data.get('role'))}")
        print("===============================")

        try:
            # ✅ Validation des champs requis
            required_fields = ['first_name', 'last_name', 'email', 'username', 'password', 'role']
            for field in required_fields:
                if not user_data.get(field) or str(user_data.get(field)).strip() == '':
                    return {'error': f'Field {field} is required and cannot be empty'}, 400

            # ✅ Validation du format email
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, user_data['email']):
                return {'error': 'Invalid email format'}, 400

            # ✅ Validation du rôle
            if user_data['role'] not in ['owner', 'voyageur']:
                return {'error': 'Role must be either "owner" or "voyageur"'}, 400

            # ✅ Vérification unicité email ET username avec gestion d'erreur
            existing_user_email = facade.get_user_by_email(user_data['email'])
            if existing_user_email:
                return {'error': 'Email already registered'}, 400

            # ✅ Vérification par username avec la nouvelle méthode facade
            existing_user_username = facade.get_user_by_username(user_data['username'])
            if existing_user_username:
                return {'error': 'Username already registered'}, 400

            # ✅ Création de l'utilisateur via facade corrigée
            new_user = facade.create_user(user_data)
            
            # ✅ Vérification que l'utilisateur a été créé correctement
            if not new_user:
                return {'error': 'Failed to create user'}, 500

            # ✅ Récupération des données pour vérification
            user_response = new_user.to_dict()
            
            print(f"✅ Utilisateur créé avec succès:")
            print(f"   - ID: {user_response.get('id')}")
            print(f"   - Username: {user_response.get('username')}")
            print(f"   - Email: {user_response.get('email')}")
            print(f"   - Role: {user_response.get('role')}")
            print("===============================")
            
            # ✅ Double vérification du rôle
            if 'role' not in user_response or user_response['role'] is None:
                print(f"⚠️ ATTENTION: Rôle manquant dans la réponse")
                # Force le rôle depuis les données d'origine
                user_response['role'] = user_data.get('role', 'voyageur')
            
            return user_response, 201

        except ValueError as ve:
            print(f"❌ Erreur de validation: {str(ve)}")
            return {'error': f'Validation error: {str(ve)}'}, 422
        except Exception as e:
            print(f"❌ Erreur lors de la création: {str(e)}")
            print(f"❌ Type d'erreur: {type(e).__name__}")
            return {'error': f'Internal server error: {str(e)}'}, 500

# --- LOGIN : POST /api/v1/users/login ---
@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """
        Connexion d'un utilisateur avec génération de JWT
        """
        data = api.payload
        
        try:
            # ✅ Validation des données d'entrée
            if not data.get('username') or not data.get('password'):
                return {'error': 'Username and password are required'}, 400

            # ✅ Recherche par email ou username avec la facade corrigée
            user = facade.get_user_by_credentials(data['username'])
            
            if not user:
                print(f"❌ Utilisateur non trouvé: {data['username']}")
                return {"error": "Mauvais identifiants"}, 401

            # ✅ Vérification du mot de passe
            if not hasattr(user, 'check_password') or not user.check_password(data['password']):
                print(f"❌ Mot de passe incorrect pour: {data['username']}")
                return {"error": "Mauvais identifiants"}, 401

            # ✅ Récupération des données utilisateur
            user_dict = user.to_dict()
            user_role = user_dict.get('role', 'voyageur')
            
            print(f"=== DEBUG LOGIN SERVEUR ===")
            print(f"✅ Utilisateur connecté: {user_dict.get('email')}")
            print(f"✅ Username: {user_dict.get('username')}")
            print(f"✅ Rôle utilisateur: '{user_role}'")
            print(f"✅ Type du rôle: {type(user_role)}")
            print(f"✅ ID utilisateur: {user_dict.get('id')}")
            print("============================")
            
            # ✅ Création du token JWT avec toutes les informations
            additional_claims = {
                "role": user_role,
                "first_name": user_dict.get('first_name', ''),
                "last_name": user_dict.get('last_name', ''),
                "email": user_dict.get('email', ''),
                "username": user_dict.get('username', ''),
                "is_admin": user_dict.get('is_admin', False)
            }
            
            # ✅ Vérification que l'ID utilisateur existe
            user_identity = user_dict.get('id')
            if not user_identity:
                print("❌ ERREUR: ID utilisateur manquant")
                return {'error': 'User ID missing'}, 500
            
            token = create_access_token(
                identity=str(user_identity),  # Convertir en string pour sécurité
                additional_claims=additional_claims
            )
            
            print(f"✅ Token JWT créé avec succès")
            print(f"✅ Claims inclus: {list(additional_claims.keys())}")
            
            # ✅ Réponse complète avec double token pour compatibilité
            response = {
                "token": token,
                "access_token": token,  # Compatibilité frontend
                "user": user_dict,
                "message": "Login successful"
            }
            
            return response, 200
            
        except Exception as e:
            print(f"❌ Erreur lors de la connexion: {str(e)}")
            print(f"❌ Type d'erreur: {type(e).__name__}")
            return {"error": "Internal server error"}, 500

# --- LISTE TOUS USERS ---
@api.route('/')
class UserList(Resource):
    @api.doc(security='jwt')
    @jwt_required()
    @api.response(200, 'List of users retrieved successfully')
    @api.marshal_list_with(user_model)
    def get(self):
        """Liste des utilisateurs (admin seulement)"""
        try:
            # ✅ Vérification des permissions admin
            claims = get_jwt()
            if not claims.get("is_admin", False):
                abort(403, "Accès réservé aux administrateurs")
            
            users = facade.get_users()
            
            # ✅ DEBUG : Affichage des utilisateurs avec leurs rôles
            print("=== LISTE UTILISATEURS ===")
            for user in users:
                user_dict = user.to_dict() if hasattr(user, 'to_dict') else user
                print(f"User: {user_dict.get('email')} | Username: {user_dict.get('username')} | Rôle: {user_dict.get('role')}")
            print(f"Total: {len(users)} utilisateurs")
            print("========================")
            
            return users, 200
            
        except Exception as e:
            print(f"❌ Erreur récupération utilisateurs: {str(e)}")
            return {'error': 'Failed to retrieve users'}, 500

# --- GET USER PAR ID ---
@api.route('/<user_id>')
class UserResource(Resource):
    @api.doc(security='jwt')
    @jwt_required()
    @api.marshal_with(user_model)
    @api.response(200, 'User retrieved successfully')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Récupération d'un utilisateur par son ID"""
        try:
            user = facade.get_user(user_id)
            if not user:
                return {'error': 'User not found'}, 404
            
            user_dict = user_id.to_dict()
            
            print(f"=== GET USER {user_id} ===")
            print(f"Email: {user_dict.get('email')}")
            print(f"Username: {user_dict.get('username')}")
            print(f"Rôle: {user_dict.get('role')}")
            print("========================")
            
            return user_dict, 200
            
        except Exception as e:
            print(f"❌ Erreur récupération utilisateur {user_id}: {str(e)}")
            return {'error': 'Failed to retrieve user'}, 500

# --- UPDATE USER ---
@api.route('/<user_id>')
class UserUpdate(Resource):
    @api.doc(security='jwt')
    @jwt_required()
    @api.expect(user_register_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(403, 'Forbidden')
    def put(self, user_id):
        """Mise à jour d'un utilisateur"""
        try:
            # ✅ Vérification des permissions
            current_user_id = get_jwt_identity()
            claims = get_jwt()
            
            # Seul l'utilisateur lui-même ou un admin peut modifier
            if str(current_user_id) != str(user_id) and not claims.get("is_admin", False):
                abort(403, "Accès non autorisé")
            
            user_data = api.payload
            updated_user = facade.update_user(user_id, user_data)
            
            if not updated_user:
                return {'error': 'User not found'}, 404
            
            return updated_user.to_dict(), 200
            
        except Exception as e:
            print(f"❌ Erreur mise à jour utilisateur: {str(e)}")
            return {'error': 'Failed to update user'}, 500

# --- DELETE USER ---
@api.route('/<user_id>')
class UserDelete(Resource):
    @api.doc(security='jwt')
    @jwt_required()
    @api.response(200, 'User deleted successfully')
    @api.response(404, 'User not found')
    @api.response(403, 'Forbidden')
    def delete(self, user_id):
        """Suppression d'un utilisateur (admin seulement)"""
        try:
            # ✅ Vérification admin obligatoire pour suppression
            claims = get_jwt()
            if not claims.get("is_admin", False):
                abort(403, "Suppression réservée aux administrateurs")
            
            success = facade.delete_user(user_id)
            if not success:
                return {'error': 'User not found'}, 404
            
            return {'message': 'User deleted successfully'}, 200
            
        except Exception as e:
            print(f"❌ Erreur suppression utilisateur: {str(e)}")
            return {'error': 'Failed to delete user'}, 500
