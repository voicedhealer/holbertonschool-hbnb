from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required

api = Namespace('places', description='Place operations')

amenity_model = api.model('PlaceAmenity', {
    'id': fields.String(),
    'name': fields.String()
})

user_model = api.model('PlaceUser', {
    'id': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String()
})

review_model = api.model('PlaceReview', {
    'id': fields.String(),
    'text': fields.String(),
    'rating': fields.Integer(),
    'user_id': fields.String()
})

place_model = api.model('Place', {
    'title': fields.String(required=True),
    'description': fields.String(),
    'price': fields.Float(required=True),
    'latitude': fields.Float(required=True),
    'longitude': fields.Float(required=True),
    'owner_id': fields.String(required=True),
    'amenities': fields.List(fields.String, required=True)
})

place_output_model = api.model('PlaceOut', {
    'id': fields.String(),
    'title': fields.String(),
    'description': fields.String(),
    'price': fields.Float(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'owner_id': fields.String(),  # <-- Ajout explicite pour les tests
    'owner': fields.Nested(user_model),
    'amenities': fields.List(fields.Nested(amenity_model)),
    'reviews': fields.List(fields.Nested(review_model))
})

def place_to_dict(place, details=True):
    data = {
        'id': str(place.id),
        'title': place.title,
        'description': place.description,
        'price': place.price,
        'latitude': place.latitude,
        'longitude': place.longitude,
        'owner_id': str(place.owner_id),  # <-- Ajout explicite pour les tests
    }
    if details:
        # Owner (si chargé)
        if hasattr(place, 'owner') and place.owner:
            data['owner'] = {
                'id': str(place.owner.id),
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            }
        else:
            data['owner'] = None
        # Amenities (via table d'association)
        if hasattr(place, 'amenities'):
            data['amenities'] = [
                {'id': str(pa.amenity.id), 'name': pa.amenity.name}
                for pa in getattr(place, 'amenities', [])
                if hasattr(pa, 'amenity') and pa.amenity
            ]
        else:
            data['amenities'] = []
        # Reviews
        if hasattr(place, 'reviews'):
            data['reviews'] = [
                {
                    'id': str(r.id),
                    'text': r.text,
                    'rating': r.rating,
                    'user_id': str(r.user_id)
                }
                for r in place.reviews
            ]
        else:
            data['reviews'] = []
    return data

@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place created')
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        data = api.payload
        try:
            place = HBnBFacade().create_place(data)
        except Exception as e:
            return {'error': str(e)}, 400
        # Retourne tous les champs attendus par les tests
        return place_to_dict(place, details=False), 201

    @api.marshal_list_with(place_output_model)
    def get(self):
        places = HBnBFacade().get_all_places()
        return [place_to_dict(p) for p in places], 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.marshal_with(place_output_model)
    def get(self, place_id):
        place = HBnBFacade().get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place_to_dict(place), 200

    @api.expect(place_model, validate=True)
    @jwt_required()
    def put(self, place_id):
        data = api.payload
        try:
            place = HBnBFacade().update_place(place_id, data)
        except Exception as e:
            return {'error': str(e)}, 400
        if not place:
            return {'error': 'Place not found'}, 404
        return place_to_dict(place), 200
