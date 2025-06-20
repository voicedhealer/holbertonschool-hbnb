"""
Module pour la gestion des endpoints de l'API concernant les 'Reviews'.

Ce fichier définit les routes et les opérations CRUD (Create, Read, Update, Delete)
pour les ressources 'Review'. Il s'appuie sur Flask-RESTX pour structurer
les endpoints, valider les données et générer la documentation Swagger.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.services import facade

# Création du namespace pour regrouper toutes les routes liées aux reviews.
review_ns = Namespace("reviews", description="Opérations relatives aux reviews (avis)")

# Définition du modèle de données pour une review.
# Ce modèle sert à la fois à la validation des données entrantes (payloads)
# et à la documentation automatique de l'API.
review_model = review_ns.model('Review', {
    'id': fields.String(readonly=True, description="L'identifiant unique de la review"),
    'user_id': fields.String(required=True, description="L'identifiant de l'utilisateur qui a posté la review"),
    'place_id': fields.String(required=True, description="L'identifiant du lieu concerné par la review"),
    'text': fields.String(required=True, description="Le contenu textuel de la review"),
    'rating': fields.Integer(required=True, description="La note attribuée par l'utilisateur, de 1 à 5"),
    'comment': fields.String(description="Un commentaire additionnel et optionnel")
})


@review_ns.route('/')
class ReviewList(Resource):
    """Gère les opérations sur la liste des reviews."""

    @review_ns.doc('list_reviews')
    @review_ns.marshal_list_with(review_model)
    def get(self):
        """
        Récupère la liste complète de toutes les reviews.

        Retourne un tableau de toutes les reviews présentes dans le système,
        chacune formatée selon le `review_model`.
        """
        return facade.get_all_reviews()

    @review_ns.doc('create_review')
    @review_ns.expect(review_model, validate=True)
    @review_ns.marshal_with(review_model, code=201)
    def post(self):
        """
        Crée une nouvelle review.

        Le corps de la requête doit être un objet JSON qui correspond au `review_model`
        (sans l'ID, qui est généré automatiquement). La validation des champs
        requis, des types de données, est automatique.

        Returns:
            tuple: Un tuple contenant la review nouvellement créée et le code
                   de statut HTTP 201 (Created).
        """
        data = request.json
        return facade.create_review(data), 201


@review_ns.route('/<string:review_id>')
@review_ns.param('review_id', "L'identifiant unique de la review")
@review_ns.response(404, 'Review non trouvée.')
class ReviewResource(Resource):
    """Gère les opérations sur une review spécifique (GET, PUT, DELETE)."""

    @review_ns.doc('get_review')
    @review_ns.marshal_with(review_model)
    def get(self, review_id):
        """
        Récupère les détails d'une review spécifique par son ID.

        Args:
            review_id (str): L'identifiant de la review à récupérer.

        Returns:
            dict: L'objet de la review si elle est trouvée.
                  Provoque une erreur 404 si l'ID n'existe pas.
        """
        review = facade.get_review(review_id)
        if not review:
            review_ns.abort(404, f"Review avec l'ID {review_id} non trouvée.")
        return review

    @review_ns.doc('update_review')
    @review_ns.expect(review_model, validate=True)
    @review_ns.marshal_with(review_model)
    def put(self, review_id):
        """
        Met à jour une review existante.

        Le corps de la requête contient les nouvelles données pour la review.
        Seuls les champs fournis dans le JSON seront mis à jour.

        Args:
            review_id (str): L'identifiant de la review à mettre à jour.

        Returns:
            dict: L'objet de la review après mise à jour.
                  Provoque une erreur 404 si l'ID n'existe pas.
        """
        data = request.json
        review = facade.update_review(review_id, data)
        if not review:
            review_ns.abort(404, f"Review avec l'ID {review_id} non trouvée.")
        return review

    @review_ns.doc('delete_review')
    @review_ns.response(204, 'Review supprimée avec succès.')
    def delete(self, review_id):
        """
        Supprime une review par son identifiant.

        En cas de succès, cette opération ne retourne aucun contenu dans le corps
        de la réponse, seulement un code de statut HTTP 204 (No Content).

        Args:
            review_id (str): L'identifiant de la review à supprimer.

        Returns:
            tuple: Une réponse vide avec un code de statut 204.
                   Provoque une erreur 404 si l'ID n'existe pas.
        """
        if not facade.delete_review(review_id):
            review_ns.abort(404, f"Review avec l'ID {review_id} non trouvée.")
        return '', 204
