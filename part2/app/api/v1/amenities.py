from flask_restx import Namespace, Resource, fields
from flask import request
from app.services.facade import HBnBFacade
from app.models.base import BaseModel

# Crée le namespace
amenity_ns = Namespace('amenities', description='Amenity operations')

# Modèle de données pour la documentation et la validation
amenity_model = amenity_ns.model('Amenity', {
    'id': fields.String(readonly=True, description='Amenity ID'),
    'name': fields.String(required=True, description='Amenity name')
})

# Instancie la façade (business logic)
facade = HBnBFacade()

@amenity_ns.route('/')
class AmenityList(Resource):
    @amenity_ns.marshal_list_with(amenity_model)
    def get(self):
        """Liste toutes les amenities"""
        return facade.get_all_amenities()

    @amenity_ns.expect(amenity_model, validate=True)
    @amenity_ns.marshal_with(amenity_model, code=201)
    def post(self):
        """Crée une nouvelle amenity"""
        data = request.json
        return facade.create_amenity(data), 201

@amenity_ns.route('/<string:amenity_id>')
@amenity_ns.response(404, 'Amenity not found')
@amenity_ns.param('amenity_id', 'L\'identifiant de l\'amenity')
class AmenityResource(Resource):
    @amenity_ns.marshal_with(amenity_model)
    def get(self, amenity_id):
        """Récupère une amenity par ID"""
        amenity = facade.get_amenity(amenity_id)
        if amenity is None:
            amenity_ns.abort(404, "Amenity not found")
        return amenity

    @amenity_ns.expect(amenity_model, validate=True)
    @amenity_ns.marshal_with(amenity_model)
    def put(self, amenity_id):
        """Met à jour une amenity"""
        data = request.json
        amenity = facade.update_amenity(amenity_id, data)
        if amenity is None:
            amenity_ns.abort(404, "Amenity not found")
        return amenity
