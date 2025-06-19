from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import HBnBFacade

place_ns = Namespace('places', description='Place operations')
facade = HBnBFacade()

# Modèle pour la documentation Swagger
place_model = place_ns.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'city': fields.String(description='City'),
    'address': fields.String(description='Address'),
    'amenities': fields.List(fields.String, description="List of amenity IDs")
})

@place_ns.route('/')
class PlaceList(Resource):
    @place_ns.expect(place_model)
    @place_ns.response(201, 'Place successfully created')
    def post(self):
        """Créer un nouveau lieu"""
        data = request.json
        place = facade.create_place(data)
        return place, 201

    @place_ns.response(200, 'Liste des lieux récupérée avec succès')
    def get(self):
        """Récupérer la liste de tous les lieux"""
        return facade.get_all_places(), 200

@place_ns.route('/<string:place_id>')
@place_ns.param('place_id', 'Identifiant du lieu')
@place_ns.response(404, 'Lieu non trouvé')
class PlaceResource(Resource):
    @place_ns.response(200, 'Lieu trouvé avec succès')
    def get(self, place_id):
        """Récupérer un lieu par ID"""
        place = facade.get_place(place_id)
        if not place:
            place_ns.abort(404, 'Lieu non trouvé')
        return place, 200

    @place_ns.expect(place_model)
    @place_ns.response(200, 'Lieu mis à jour avec succès')
    def put(self, place_id):
        """Mettre à jour un lieu"""
        data = request.json
        updated = facade.update_place(place_id, data)
        if not updated:
            place_ns.abort(404, 'Lieu non trouvé')
        return updated, 200






