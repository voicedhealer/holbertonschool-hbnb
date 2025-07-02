# app/api/v1/users.py

from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import HBnBFacade

api = Namespace('users', description='User operations')
facade = HBnBFacade()

# ✅ Définition du modèle d'entrée (sans max_length)
user_model = api.model('User', {
    'first_name': fields.String(required=True, description="Prénom de l'utilisateur"),
    'last_name': fields.String(required=True, description="Nom de l'utilisateur"),
    'email': fields.String(required=True, description="Adresse email"),
    'password': fields.String(required=True, description="Mot de passe"),
    'is_admin': fields.Boolean(required=False, description="Est administrateur ?")
})

# ✅ Modèle de sortie (sans le mot de passe)
user_output = api.model('UserOutput', {
    'id': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'is_admin': fields.Boolean
})


@api.route('/')
class UserListResource(Resource):
    @api.marshal_list_with(user_output)
    def get(self):
        """Liste tous les utilisateurs"""
        return facade.get_users()

    @api.expect(user_model)
    @api.marshal_with(user_output, code=201)
    def post(self):
        """Crée un nouvel utilisateur"""
        user_data = request.get_json()

        # ✅ Validation manuelle possible
        if len(user_data.get('password', '')) < 6:
            return {'error': 'Le mot de passe doit contenir au moins 6 caractères.'}, 400

        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            return {'error': 'Email déjà enregistré'}, 400

        new_user = facade.create_user(user_data)
        return new_user, 201


@api.route('/<string:user_id>')
@api.param('user_id', 'Identifiant de l\'utilisateur')
class UserResource(Resource):
    @api.marshal_with(user_output)
    def get(self, user_id):
        """Récupère un utilisateur par ID"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'Utilisateur non trouvé'}, 404
        return user

    @api.expect(user_model)
    def put(self, user_id):
        """Met à jour un utilisateur"""
        user_data = request.get_json()
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'Utilisateur non trouvé'}, 404

        facade.update_user(user_id, user_data)
        return {'message': 'Utilisateur mis à jour'}
