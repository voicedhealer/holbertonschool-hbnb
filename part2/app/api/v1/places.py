from app.models.base import BaseModel
from datetime import datetime
from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade

place_ns = Namespace('places', description='Place operations')

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

# Ceci doit être en dehors de la classe précédente
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

api = Namespace('places', description='Place operations')

# Define the models for related entities
amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = api.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

# Define the place model for input validation and documentation
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new place"""
        # Placeholder for the logic to register a new place
        pass

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        # Placeholder for logic to return a list of all places
        pass

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID"""
        # Placeholder for the logic to retrieve a place by ID, including associated owner and amenities
        pass

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information"""
        # Placeholder for the logic to update a place by ID
        pass
