"""
Module Flask-RESTX pour la gestion des utilisateurs.

Ce module expose une API RESTful permettant de créer, lister, récupérer et mettre à jour des utilisateurs.
Les réponses et les entrées sont validées et documentées automatiquement grâce à Flask-RESTX.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='Opérations sur les utilisateurs')

# Modèle utilisateur pour la validation des entrées et la documentation Swagger
user_model = api.model('User', {
    'id': fields.String(readonly=True, description='Identifiant unique de l\'utilisateur'),
    'first_name': fields.String(required=True, description='Prénom de l\'utilisateur'),
    'last_name': fields.String(required=True, description='Nom de famille de l\'utilisateur'),
    'email': fields.String(required=True, description='Adresse email de l\'utilisateur')
})

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model, code=201)
    @api.response(201, 'Utilisateur créé avec succès')
    @api.response(400, 'Email déjà enregistré')
    def post(self):
        """
        Créer un nouvel utilisateur.

        Vérifie l'unicité de l'email avant la création.
        Retourne l'utilisateur créé.
        """
        user_data = api.payload
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            api.abort(400, "Email déjà enregistré")
        new_user = facade.create_user(user_data)
        return new_user, 201

    @api.marshal_list_with(user_model)
    @api.response(200, 'Liste des utilisateurs récupérée avec succès')
    def get(self):
        """
        Lister tous les utilisateurs.

        Retourne la liste complète des utilisateurs enregistrés.
        """
        users = facade.list_users()
        return users, 200

@api.route('/<string:user_id>')
@api.param('user_id', 'Identifiant unique de l\'utilisateur')
class UserResource(Resource):
    @api.marshal_with(user_model)
    @api.response(200, 'Détails de l\'utilisateur récupérés avec succès')
    @api.response(404, 'Utilisateur non trouvé')
    def get(self, user_id):
        """
        Récupérer les détails d'un utilisateur par son identifiant.
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, "Utilisateur non trouvé")
        return user, 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model)
    @api.response(200, 'Utilisateur mis à jour avec succès')
    @api.response(404, 'Utilisateur non trouvé')
    def put(self, user_id):
        """
        Mettre à jour les informations d'un utilisateur par son identifiant.
        """
        user_data = api.payload
        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            api.abort(404, "Utilisateur non trouvé")
        return updated_user, 200
