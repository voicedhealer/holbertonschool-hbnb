from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True)
})

amenity_output_model = api.model('AmenityOut', {
    'id': fields.String(),
    'name': fields.String()
})

def amenity_to_dict(amenity):
    return {
        'id': amenity.id,
        'name': amenity.name
    }

@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity created')
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        data = api.payload
        try:
            amenity = HBnBFacade().create_amenity(data)
        except Exception as e:
            return {'error': str(e)}, 400
        return amenity_to_dict(amenity), 201

    @api.marshal_list_with(amenity_output_model)
    def get(self):
        amenities = HBnBFacade().get_all_amenities()
        return [amenity_to_dict(a) for a in amenities], 200

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    @api.marshal_with(amenity_output_model)
    def get(self, amenity_id):
        amenity = HBnBFacade().get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity_to_dict(amenity), 200

    @api.expect(amenity_model, validate=True)
    @jwt_required()
    def put(self, amenity_id):
        data = api.payload
        try:
            amenity = HBnBFacade().update_amenity(amenity_id, data)
        except Exception as e:
            return {'error': str(e)}, 400
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity_to_dict(amenity), 200
