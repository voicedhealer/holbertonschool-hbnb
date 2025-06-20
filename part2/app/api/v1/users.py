"""
Module Flask-RESTX pour la gestion des utilisateurs.

Ce module expose une API RESTful permettant de créer, lister, récupérer et
mettre à jour des utilisateurs. Les réponses et les entrées sont validées et
documentées automatiquement grâce à Flask-RESTX.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.services import facade
from app.models.base import BaseModel

# Création du namespace pour les opérations relatives aux utilisateurs.
api = Namespace('users', description='Opérations sur les utilisateurs')

# Modèle de données pour la validation et la documentation Swagger.
# Il définit la structure attendue pour un utilisateur dans les requêtes
# et les réponses de l'API.
user_model = api.model('User', {
    'id': fields.String(readonly=True, description="L'identifiant unique de l'utilisateur"),
    'first_name': fields.String(required=True, description="Le prénom de l'utilisateur"),
    'last_name': fields.String(required=True, description="Le nom de famille de l'utilisateur"),
    'email': fields.String(required=True, description="L'adresse email unique de l'utilisateur")
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
    """Gère la création et le listage de la collection d'utilisateurs."""

    @api.doc('create_user')
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model, code=201)
    @api.response(201, 'Utilisateur créé avec succès')
    @api.response(400, 'Email déjà enregistré')
    def post(self):
        """
        Crée un nouvel utilisateur.

        Vérifie l'unicité de l'email avant la création.
        Retourne l'utilisateur créé.
        """
        user_data = api.payload
        existing_user = facade.get_user_by_email(user_data['email'])
        if existing_user:
            api.abort(400, "Email déjà enregistré")
        new_user = facade.create_user(user_data)
        return new_user, 201

    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    @api.response(200, 'Liste des utilisateurs récupérée avec succès.')
    def get(self):
        """
        Récupère et retourne la liste de tous les utilisateurs.

        Cette route ne prend aucun paramètre et renvoie un tableau contenant
        tous les utilisateurs enregistrés dans le système.
        """
        return facade.list_users(), 200

@api.route('/<string:user_id>')
@api.param('user_id', "L'identifiant unique de l'utilisateur")
@api.response(404, 'Utilisateur non trouvé.')
class UserResource(Resource):
    """Gère les opérations sur un utilisateur spécifique via son ID."""

    @api.doc('get_user')
    @api.marshal_with(user_model)
    @api.response(200, "Détails de l'utilisateur récupérés avec succès.")
    def get(self, user_id):
        """
        Récupère les détails d'un utilisateur par son ID.

        Args:
            user_id (str): L'identifiant de l'utilisateur à récupérer,
                           fourni dans le chemin de l'URL.

        Returns:
            tuple: Un tuple contenant l'objet utilisateur et le code de statut 200.
                   Provoque une erreur 404 si l'ID n'est pas trouvé.
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, f"Utilisateur avec l'ID {user_id} non trouvé.")
        return user, 200

    @api.doc('update_user')
    @api.expect(user_model, validate=True)
    @api.marshal_with(user_model)
    @api.response(200, 'Utilisateur mis à jour avec succès')
    @api.response(404, 'Utilisateur non trouvé')
    def put(self, user_id):
        """
        Met à jour les informations d'un utilisateur existant.

        Cette méthode remplace les données de l'utilisateur par celles fournies
        dans le corps de la requête. L'email ne peut généralement pas être modifié
        via cette route pour éviter les conflits d'unicité.

        Args:
            user_id (str): L'identifiant de l'utilisateur à mettre à jour.

        Payload:
            dict: Un objet JSON avec les nouvelles données de l'utilisateur.

        Returns:
            tuple: Un tuple contenant l'objet utilisateur mis à jour et le code 200.
                   Provoque une erreur 404 si l'ID n'est pas trouvé.
        """
        user_data = api.payload

        # Validation personnalisée
        errors = validate_user_data(user_data)
        if errors:
            api.abort(400, " ; ".join(errors))

        updated_user = facade.update_user(user_id, user_data)
        if not updated_user:
            api.abort(404, f"Utilisateur avec l'ID {user_id} non trouvé.")
        return updated_user, 200
user_ns = api
