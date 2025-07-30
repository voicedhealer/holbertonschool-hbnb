from flask_restx import Namespace, Resource, fields
from flask import g, request
from app.services import facade

api = Namespace('places', description='Place operations')

# MODELES SWAGGER
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

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    # owner_id n'est PAS demandé par l'API, il vient du token !
    'owner': fields.Nested(user_model, description='Owner details'),
    'amenities': fields.List(fields.String, required=True, description="List of amenities ID's")
})

############ AUTH DECORATORS ############
def require_auth(fn):
    """
    Décorateur minimal. À ADAPTER avec ton vrai système JWT.
    Place l'utilisateur courant dans g.current_user.
    """
    def wrapper(*args, **kwargs):
        import jwt
        auth = request.headers.get('Authorization', None)
        if not auth or not auth.startswith('Bearer '):
            return {'error': 'Missing or invalid Authorization header'}, 401
        try:
            token = auth.split(" ")[1]
            # !! Remplace "VOTRE_CLE_SECRETE" par la vraie
            payload = jwt.decode(token, "VOTRE_CLE_SECRETE", algorithms=["HS256"])
            g.current_user = {
                'id': payload['sub'],  # ou payload['user_id'] selon ton JWT
                'role': payload.get('role', "voyageur")  # Doit être "owner" ou "voyageur"
            }
        except Exception as e:
            return {'error': 'Invalid token'}, 401
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def require_owner(fn):
    """
    Décorateur : N'autorise QUE les propriétaires (role == 'owner')
    """
    def wrapper(*args, **kwargs):
        user = g.current_user
        if user['role'] != 'owner':
            return {'error': 'Forbidden: only owners can perform this action'}, 403
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

def get_current_user():
    return g.current_user

############## ROUTES ##################
@api.route('/')
class PlaceList(Resource):
    @require_auth
    @require_owner    # <--- contrôle ici !
    @api.expect(place_model)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Forbidden')
    def post(self):
        """Register a new place (propriétaire uniquement)"""
        current_user = get_current_user()
        place_data = api.payload
        place_data["owner_id"] = current_user["id"]  # owner_id vient toujours du token, JAMAIS du front
        try:
            new_place = facade.create_place(place_data)
            return new_place.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400

    @require_auth
    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places (ou visibles selon ton modèle)"""
        places = facade.get_all_places()
        return [place.to_dict() for place in places], 200

@api.route('/<place_id>')
class PlaceResource(Resource):
    @require_auth
    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place.to_dict(), 200

    @require_auth
    @require_owner
    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Forbidden')
    def put(self, place_id):
        """Update a place's information"""
        current_user = get_current_user()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner_id != current_user["id"]:
            return {'error': "Forbidden: only owner's own place can be updated"}, 403
        try:
            place_data = api.payload
            facade.update_place(place_id, place_data)
            return {'message': 'Place updated successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 400

    @require_auth
    @require_owner
    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized - You can only delete your own places')
    def delete(self, place_id):
        """Delete a place by ID"""
        current_user = get_current_user()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner_id != current_user["id"]:
            return {'error': 'Unauthorized - You can only delete your own places'}, 403
        try:
            facade.delete_place(place_id)
            return {'message': 'Place deleted successfully'}, 200
        except Exception as e:
            return {'error': 'Internal server error'}, 500

@api.route('/<place_id>/amenities')
class PlaceAmenities(Resource):
    @require_auth
    @require_owner
    @api.expect(amenity_model)
    @api.response(200, 'Amenities added successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Forbidden')
    def post(self, place_id):
        current_user = get_current_user()
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        if place.owner_id != current_user["id"]:
            return {'error': "Forbidden"}, 403

        amenities_data = api.payload
        if not amenities_data or len(amenities_data) == 0:
            return {'error': 'Invalid input data'}, 400

        for amenity in amenities_data:
            a = facade.get_amenity(amenity['id'])
            if not a:
                return {'error': 'Invalid input data'}, 400

        for amenity in amenities_data:
            place.add_amenity(amenity)
        return {'message': 'Amenities added successfully'}, 200

@api.route('/<place_id>/reviews/')
class PlaceReviewList(Resource):
    @require_auth
    @api.response(200, 'List of reviews for the place retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return [review.to_dict() for review in place.reviews], 200
