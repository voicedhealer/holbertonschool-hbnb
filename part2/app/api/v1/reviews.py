from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade


# Création du namespace pour toutes les routes liées aux reviews
review_ns = Namespace("reviews", description="Reviews operations")

# Définition du modèle de données pour une review (pour validation et documentation Swagger)
review_model = review_ns.model('Review', {
    'id': fields.String(readonly=True, description='Review ID'),  # ID unique de la review
    'user_id': fields.String(required=True, description="ID of the user"),  # ID de l'utilisateur
    'place_id': fields.String(required=True, description="ID of the place"),  # ID du lieu
    'text': fields.String(required=True, description="Text content of the review"),  # Contenu de la review
    'rating': fields.Integer(required=True, description="Rating from 1 to 5"),  # Note de 1 à 5
    'comment': fields.String(description="Optional comment")  # Commentaire optionnel
})

# Route pour gérer la collection de reviews (GET toutes, POST une nouvelle)
@review_ns.route('/')
class ReviewList(Resource):
    @review_ns.marshal_list_with(review_model)
    def get(self):
        """Liste toutes les reviews"""
        # Appelle la façade pour récupérer toutes les reviews
        return facade.get_all_reviews()

    @review_ns.expect(review_model, validate=True)
    @review_ns.marshal_with(review_model, code=201)
    def post(self):
        """Crée une nouvelle review"""
        data = request.json  # Récupère les données envoyées par le client
        # Appelle la façade pour créer la review et retourne la réponse
        return facade.create_review(data), 201

# Route pour gérer une review individuelle (GET, PUT, DELETE par ID)
@review_ns.route('/<string:review_id>')
class ReviewResource(Resource):
    @review_ns.marshal_with(review_model)
    def get(self, review_id):
        """Récupère une review par ID"""
        # Appelle la façade pour récupérer la review
        review = facade.get_review(review_id)
        if not review:
            # Si la review n'existe pas, retourne une erreur 404
            review_ns.abort(404, "Review not found")
        return review

    @review_ns.expect(review_model, validate=True)
    @review_ns.marshal_with(review_model)
    def put(self, review_id):
        """Met à jour une review"""
        data = request.json  # Données de mise à jour
        # Appelle la façade pour mettre à jour la review
        review = facade.update_review(review_id, data)
        if not review:
            # Si la review n'existe pas, retourne une erreur 404
            review_ns.abort(404, "Review not found")
        return review

    def delete(self, review_id):
        """Supprime une review"""
        # Appelle la façade pour supprimer la review
        deleted = facade.delete_review(review_id)
        if not deleted:
            # Si la review n'existe pas, retourne une erreur 404
            review_ns.abort(404, "Review not found")
        # Retourne un code 204 (No Content) si la suppression a réussi
        return '', 204
