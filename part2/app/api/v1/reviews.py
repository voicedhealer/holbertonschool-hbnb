from flask_restx import Namespace, Resource, fields
from app.models.review import Review
from flask import request

# On crée un namespace pour regrouper toutes les routes liées aux reviews
reviews_ns = Namespace('reviews', description='Operations related to reviews')

# On crée une liste vide pour simuler une base de données temporaire
review_storage = []

# On définit le modèle (le format) que chaque review doit suivre
# Cela sert pour valider les données entrantes et générer la doc Swagger
review_model = reviews_ns.model('Review', {
    'user_id': fields.String(required=True, description="ID of the user"),  # l'utilisateur qui a posté la review
    'place_id': fields.String(required=True, description="ID of the place"),  # le lieu concerné
    'text': fields.String(required=True, description="Text content of the review"),  # le contenu de la review
    'rating': fields.Integer(required=True, description="Rating from 1 to 5"),  # la note
    'comment': fields.String(required=False, description="Optional comment")  # commentaire facultatif
})

# On définit une ressource pour gérer la route GET /reviews
class ReviewListResource(Resource):

    # On utilise un décorateur pour dire : "on renvoie une liste de review_model"
    @reviews_ns.marshal_list_with(review_model)
    def get(self):
        """Renvoyer toutes les reviews enregistrées (en mémoire)"""
        
        # On retourne chaque review convertie en dictionnaire (car Review est une classe)
        # __dict__ transforme les attributs de l'objet en dictionnaire JSON-compatible
        return [review.__dict__ for review in review_storage]

    @reviews_ns.expect(review_model, validate=True)
    @reviews_ns.response(201, 'Review created successfully')
    def post(self):
        """Ajouter une review (temporairement en mémoire)"""
        data = request.json
        new_review = Review(**data)
        review_storage.append(new_review)
        return new_review.__dict__, 201
