"""
Module Flask-RESTX pour la gestion des utilisateurs.

Ce module expose une API RESTful permettant de créer, lister, récupérer et
mettre à jour des utilisateurs. Les réponses et les entrées sont validées et
documentées automatiquement grâce à Flask-RESTX.
"""
from flask_restx import Namespace, Resource, fields
from app.services import facade
import re

api = Namespace('users', description='Opérations sur les utilisateurs')

# Modèle utilisateur pour la validation des entrées et la documentation Swagger
user_model = api.model('User', {
    'id': fields.String(readonly=True, description="Identifiant unique de l'utilisateur"),
    'first_name': fields.String(required=True, description="Prénom de l'utilisateur"),
    'last_name': fields.String(required=True, description="Nom de famille de l'utilisateur"),
    'email': fields.String(required=True, description="Adresse email de l'utilisateur")
})

def is_valid_email(email):
    # Expression régulière simple pour valider un email
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validate_user_data(user_data):
    errors = []
    if not user_data.get('first_name') or not user_data['first_name'].strip():
        errors.append("Le prénom ne peut pas être vide.")
    if not user_data.get('last_name') or not user_data['last_name'].strip():
        errors.append("Le nom de famille ne peut pas être vide.")
    if not user_data.get('email') or not is_valid_email(user_data['email']):
        errors.append("L'adresse email est invalide.")
    return errors

@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model, code=201)
    @api.response(201, 'Utilisateur créé avec succès')
    @api.response(400, 'Données invalides ou email déjà enregistré')
    def post(self):
        print("DEBUG: POST /api/v1/users/ called")
        """
        Créer un nouvel utilisateur.
        Vérifie l'unicité de l'email et la validité des champs avant la création.
        Retourne l'utilisateur créé.
        """
        user_data = api.payload

        # Validation personnalisée
        errors = validate_user_data(user_data)
        if errors:
            api.abort(400, " ; ".join(errors))

        # Vérification de l'unicité de l'email
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            api.abort(400, "Email déjà enregistré")

        try:
            new_user = facade.create_user(user_data)
        except Exception as e:
            api.abort(500, f"Erreur interne lors de la création de l'utilisateur : {e}")

        # Vérification finale de la structure du retour
        if not isinstance(new_user, dict) or 'id' not in new_user:
            api.abort(500, "Erreur interne : l'utilisateur créé n'a pas d'identifiant.")

        print("DEBUG new_user:", new_user)
        return new_user, 201

    @api.marshal_list_with(user_model)
    @api.response(200, 'Liste des utilisateurs récupérée avec succès')
    def get(self):
        """
        Lister tous les utilisateurs.
        Retourne la liste complète des utilisateurs enregistrés.
        """
        users = facade.list_users()
        # S'assurer que chaque utilisateur est un dict avec 'id'
        users = [u for u in users if isinstance(u, dict) and 'id' in u]
        return users, 200

@api.route('/<string:user_id>')
@api.param('user_id', "Identifiant unique de l'utilisateur")
class UserResource(Resource):
    @api.marshal_with(user_model)
    @api.response(200, 'Détails de l\'utilisateur récupérés avec succès')
    @api.response(404, 'Utilisateur non trouvé')
    def get(self, user_id):
        """
        Récupérer les détails d'un utilisateur par son identifiant.
        """
        user = facade.get_user(user_id)
        if not user or 'id' not in user:
            api.abort(404, "Utilisateur non trouvé")
        return user, 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model)
    @api.response(200, 'Utilisateur mis à jour avec succès')
    @api.response(404, 'Utilisateur non trouvé')
    @api.response(400, 'Données invalides')
    def put(self, user_id):
        """
        Mettre à jour les informations d'un utilisateur par son identifiant.
        """
        user_data = api.payload

        # Validation personnalisée
        errors = validate_user_data(user_data)
        if errors:
            api.abort(400, " ; ".join(errors))

        updated_user = facade.update_user(user_id, user_data)
        if not updated_user or 'id' not in updated_user:
            api.abort(404, "Utilisateur non trouvé")
        return updated_user, 200

user_ns = api