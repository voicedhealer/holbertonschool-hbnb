from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

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
    'owner_id': fields.String(),
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
        'owner_id': str(place.owner_id),
    }
    if details:
        if hasattr(place, 'owner') and place.owner:
            data['owner'] = {
                'id': str(place.owner.id),
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            }
        else:
            data['owner'] = None
        if hasattr(place, 'amenities'):
            data['amenities'] = [
                {'id': str(pa.amenity.id), 'name': pa.amenity.name}
                for pa in getattr(place, 'amenities', [])
                if hasattr(pa, 'amenity') and pa.amenity
            ]
        else:
            data['amenities'] = []
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
    @api.response(400, 'Invalid input or duplicate location')
    @jwt_required()
    def post(self):
        data = api.payload

        # Vérification unicité géolocalisation
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        existing_place = HBnBFacade().find_place_by_location(latitude, longitude)
        if existing_place:
            return {'error': 'A place already exists at this location'}, 400

        try:
            place = HBnBFacade().create_place(data)
        except Exception as e:
            return {'error': str(e)}, 400
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
        claims = get_jwt()
        user_id = claims.get('sub')
        is_admin = claims.get('is_admin', False)

        place = HBnBFacade().get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        # Vérification des droits : admin ou owner uniquement
        if not (is_admin or str(place.owner_id) == user_id):
            return {'error': 'Permission denied'}, 403

        data = api.payload

        # Optionnel : éviter de modifier la géolocalisation vers un lieu déjà existant
        new_lat = data.get('latitude', place.latitude)
        new_lon = data.get('longitude', place.longitude)
        if (new_lat != place.latitude or new_lon != place.longitude):
            exist = HBnBFacade().find_place_by_location(new_lat, new_lon)
            if exist and exist.id != place.id:
                return {'error': 'Another place already exists at the new location'}, 400

        try:
            updated_place = HBnBFacade().update_place(place_id, data)
        except Exception as e:
            return {'error': str(e)}, 400

        if not updated_place:
            return {'error': 'Place not found'}, 404
        return place_to_dict(updated_place), 200
