from app.models.base import BaseModel
from datetime import datetime
from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import HBnBFacade

place_ns = Namespace('places', description='Place operations')
facade = HBnBFacade()

place_model = place_ns.model('Place', {
    'name': fields.String(required=True),
    'description': fields.String,
    'city': fields.String,
    'address': fields.String,
    'price': fields.Float,
    'owner_id': fields.String,
    'reviews': fields.List(fields.String, description='List of review IDs')
})

@place_ns.route('/')
class PlaceList(Resource):
    @place_ns.expect(place_model, validate=True)
    @place_ns.response(201, 'Place created successfully')
    def post(self):
        """Créer un nouveau lieu"""
        data = request.json
        place = facade.create_place(data)
        return place, 201

    @place_ns.response(200, 'Liste des lieux récupérée avec succès')
    def get(self):
        """Récupérer la liste de tous les lieux"""
        places = facade.get_all_places()
        return places, 200

# 👇 Ceci doit être en dehors de la classe précédente
@place_ns.route('/<string:place_id>')
@place_ns.response(404, 'Lieu non trouvé')
@place_ns.param('place_id', 'Identifiant du lieu')
class PlaceResource(Resource):
    @place_ns.response(200, 'Lieu trouvé avec succès')
    def get(self, place_id):
        """Récupérer un lieu par son ID"""
        place = facade.get_place(place_id)
        if not place:
            place_ns.abort(404, 'Lieu non trouvé')
        reviews = [r['id'] for r in facade.get_all_reviews() if r['place_id'] == place_id]
        place['reviews'] = reviews
        return place, 200