"""
Module gérant les endpoints de l'API pour les ressources 'Place'.

Ce fichier définit les routes et les opérations CRUD (Create, Read, Update)
pour les lieux (Places). Il utilise Flask-RESTX pour structurer l'API,
valider les données entrantes et formater les réponses.
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from app.services import facade

# Création du namespace pour les opérations sur les lieux.
# 'places' sera le préfixe de l'URL (ex: /api/places).
place_ns = Namespace('places', description='Opérations relatives aux lieux')

# Modèle de données utilisé pour la validation des requêtes et la
# documentation automatique de l'API (Swagger UI).
place_model = place_ns.model('Place', {
    'title': fields.String(required=True, description='Le titre ou nom du lieu.'),
    'description': fields.String(description='Une description détaillée du lieu.'),
    'price': fields.Float(required=True, description='Le prix par nuit.'),
    'latitude': fields.Float(required=True, description='La latitude géographique du lieu.'),
    'longitude': fields.Float(required=True, description='La longitude géographique du lieu.'),
    'owner_id': fields.String(required=True, description="L'identifiant du propriétaire (User)."),
    'city': fields.String(description='La ville où se situe le lieu.'),
    'address': fields.String(description="L'adresse complète du lieu."),
    'amenities': fields.List(fields.String, description="Liste des identifiants des 'amenities' associées.")
})


@place_ns.route('/')
class PlaceList(Resource):
    """Gère les opérations sur la collection de lieux (création et listage)."""

    @place_ns.doc('create_place')
    @place_ns.expect(place_model, validate=True)
    @place_ns.response(201, 'Lieu créé avec succès.')
    def post(self):
        """
        Crée un nouveau lieu.

        Le corps de la requête doit contenir un objet JSON conforme au `place_model`.
        La validation des données est gérée automatiquement par Flask-RESTX.
        En cas de succès, retourne les données du lieu nouvellement créé avec un
        code de statut HTTP 201.
        """
        data = request.json
        place = facade.create_place(data)
        return place, 201

    @place_ns.doc('list_places')
    @place_ns.response(200, 'Liste des lieux récupérée avec succès.')
    def get(self):
        """
        Récupère et retourne la liste de tous les lieux.

        Cette route ne nécessite aucun paramètre et renvoie un tableau
        contenant tous les lieux enregistrés dans la base de données.
        """
        return facade.get_all_places(), 200


@place_ns.route('/<string:place_id>')
@place_ns.param('place_id', 'L\'identifiant unique du lieu.')
@place_ns.response(404, 'Lieu non trouvé.')
class PlaceResource(Resource):
    """Gère les opérations sur un lieu spécifique, identifié par son ID."""

    @place_ns.doc('get_place')
    @place_ns.response(200, 'Lieu trouvé avec succès.')
    def get(self, place_id):
        """
        Récupère les informations d'un lieu spécifique par son ID.

        Args:
            place_id (str): L'identifiant du lieu à récupérer, passé dans l'URL.

        Returns:
            dict: Un dictionnaire contenant les détails du lieu.
                  Retourne une erreur 404 si aucun lieu ne correspond à l'ID.
        """
        place = facade.get_place(place_id)
        if not place:
            place_ns.abort(404, f'Lieu avec l\'ID {place_id} non trouvé.')
        return place, 200

    @place_ns.doc('update_place')
    @place_ns.expect(place_model, validate=True)
    @place_ns.response(200, 'Lieu mis à jour avec succès.')
    def put(self, place_id):
        """
        Met à jour les informations d'un lieu existant.

        Le corps de la requête doit contenir un objet JSON avec les champs
        à mettre à jour, conformément au `place_model`.

        Args:
            place_id (str): L'identifiant du lieu à mettre à jour.

        Returns:
            dict: Les données du lieu mis à jour.
                  Retourne une erreur 404 si aucun lieu ne correspond à l'ID.
        """
        data = request.json
        updated = facade.update_place(place_id, data)
        if not updated:
            place_ns.abort(404, f'Lieu avec l\'ID {place_id} non trouvé.')
        return updated, 200
