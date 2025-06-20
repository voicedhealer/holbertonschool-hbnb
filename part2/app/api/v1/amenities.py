"""
Module pour la gestion des endpoints de l'API concernant les 'Amenities'.

Ce fichier définit les routes et les opérations CRUD (Create, Read, Update)
pour les ressources 'Amenity' en utilisant Flask-RESTX.
Il expose des endpoints pour lister, créer, récupérer, et mettre à jour
des amenities.
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from app.services import facade

# Crée un namespace pour regrouper les routes relatives aux amenities.
# Le namespace est un concept de Flask-RESTX pour organiser les endpoints.
amenity_ns = Namespace('amenities', description='Opérations relatives aux amenities')

# Modèle de données pour la documentation (Swagger) et la validation des entrées/sorties.
# 'readonly=True' pour l'ID signifie qu'il est généré par le serveur et non fourni par le client.
amenity_model = amenity_ns.model('Amenity', {
    'id': fields.String(readonly=True, description="L'identifiant unique de l'amenity"),
    'name': fields.String(required=True, description="Le nom de l'amenity")
})

@amenity_ns.route('/')
class AmenityList(Resource):
    """Gère les opérations sur la liste des amenities."""

    @amenity_ns.doc('list_amenities')
    @amenity_ns.marshal_list_with(amenity_model)
    def get(self):
        """
        Récupère et renvoie la liste complète de toutes les amenities.

        Cette méthode ne prend aucun paramètre et retourne un tableau d'objets
        Amenity, chacun formaté selon l'amenity_model.
        """
        return facade.get_all_amenities()

    @amenity_ns.doc('create_amenity')
    @amenity_ns.expect(amenity_model, validate=True)
    @amenity_ns.marshal_with(amenity_model, code=201)
    def post(self):
        """
        Crée une nouvelle amenity.

        Le corps de la requête doit contenir un objet JSON correspondant à
        l'amenity_model (sans l'ID). La validation est automatique.
        En cas de succès, renvoie la nouvelle amenity créée avec son ID
        et un statut HTTP 201 Created.
        """
        data = request.json
        return facade.create_amenity(data), 201


@amenity_ns.route('/<string:amenity_id>')
@amenity_ns.response(404, 'Amenity non trouvée')
@amenity_ns.param('amenity_id', "L'identifiant de l'amenity")
class AmenityResource(Resource):
    """Gère les opérations sur une amenity spécifique identifiée par son ID."""

    @amenity_ns.doc('get_amenity')
    @amenity_ns.marshal_with(amenity_model)
    def get(self, amenity_id):
        """
        Récupère les détails d'une amenity spécifique par son ID.

        Args:
            amenity_id (str): L'identifiant unique de l'amenity à récupérer.

        Returns:
            dict: L'objet amenity correspondant à l'ID, formaté par l'amenity_model.
                  Retourne une erreur 404 si l'ID n'est pas trouvé.
        """
        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            amenity_ns.abort(404, f"Amenity avec l'ID {amenity_id} non trouvée.")
        return amenity

    @amenity_ns.doc('update_amenity')
    @amenity_ns.expect(amenity_model, validate=True)
    @amenity_ns.marshal_with(amenity_model)
    def put(self, amenity_id):
        """
        Met à jour une amenity existante.

        Le corps de la requête doit contenir les nouvelles données de l'amenity.
        Seuls les champs fournis seront mis à jour.

        Args:
            amenity_id (str): L'identifiant de l'amenity à mettre à jour.

        Returns:
            dict: L'objet amenity mis à jour.
                  Retourne une erreur 404 si l'ID n'est pas trouvé.
        """
        data = request.json
        amenity = facade.update_amenity(amenity_id, data)
        if amenity is None:
            amenity_ns.abort(404, f"Amenity avec l'ID {amenity_id} non trouvée.")
        return amenity
