from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('places', description='Place operations')


# Modèles pour Swagger / validation
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
    'amenities': fields.List(fields.String, required=True)
})

place_output_model = api.model('PlaceOut', {
    'id': fields.String(),
    'name': fields.String(),
    'description': fields.String(),
    'price_by_night': fields.Float(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'owner_id': fields.String(),
    'host_name': fields.String(),
    'city_name': fields.String(),
    'owner': fields.Nested(user_model),
    'amenities': fields.List(fields.Nested(amenity_model)),
    'reviews': fields.List(fields.Nested(review_model))
})


def place_to_dict(place, details=True):
    host_name = "Inconnu"
    if hasattr(place, 'owner') and place.owner:
        host_name = f"{place.owner.first_name} {place.owner.last_name}".strip()

    data = {
        'id': str(place.id),
        'name': place.title,
        'description': place.description,
        'price_by_night': place.price,
        'latitude': place.latitude,
        'longitude': place.longitude,
        'owner_id': str(place.owner_id),
        'host_name': host_name,
        'city_name': getattr(place, 'city_name', ''),
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
        from flask_jwt_extended import get_jwt_identity

        current_user_id = get_jwt_identity()
        if not current_user_id:
            return {'error': 'User identification failed'}, 401

        data = api.payload.copy()
        data['owner_id'] = current_user_id

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

    # --- AJOUT DE LA MÉTHODE DELETE ---
    @jwt_required()
    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized')
    def delete(self, place_id):
        """
        Delete a place (only owner allowed)
        """
        facade = HBnBFacade()

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        user_claims = get_jwt()
        current_user_id = user_claims.get('sub')
        if not current_user_id or str(place.owner_id) != str(current_user_id):
            return {'error': 'Unauthorized - You can only delete your own places'}, 403

        try:
            facade.delete_place(place_id)
            return {'message': 'Place deleted successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/<place_id>/amenities')
class PlaceAmenities(Resource):
    @api.expect(amenity_model)
    @api.response(200, 'Amenities added successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def post(self, place_id):
        amenities_data = api.payload
        if not amenities_data or len(amenities_data) == 0:
            return {'error': 'Invalid input data'}, 400

        place = HBnBFacade().get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        for amenity in amenities_data:
            a = HBnBFacade().get_amenity(amenity['id'])
            if not a:
                return {'error': 'Invalid input data'}, 400

        for amenity in amenities_data:
            place.add_amenity(amenity)
        return {'message': 'Amenities added successfully'}, 200


@api.route('/<place_id>/reviews/')
class PlaceReviewsList(Resource):
    def get(self, place_id):
        """Get all reviews for a place"""
        reviews = HBnBFacade().get_reviews_by_place(place_id)
        if reviews is None:
            return {'error': 'Place not found'}, 404

        # Formatage reviews
        formatted_reviews = []
        for review in reviews:
            review_data = {
                'id': str(review.id),
                'text': review.text,
                'rating': review.rating,
                'user_id': str(review.user_id),
                'user_name': "Utilisateur inconnu"
            }

            if hasattr(review, 'user') and review.user:
                review_data['user_name'] = f"{review.user.first_name} {review.user.last_name}".strip()
            else:
                try:
                    user = HBnBFacade().get_user(str(review.user_id))
                    if user:
                        review_data['user_name'] = f"{user.first_name} {user.last_name}".strip()
                except:
                    pass

            formatted_reviews.append(review_data)

        return formatted_reviews, 200

    @api.expect({'text': fields.String(required=True), 'rating': fields.Integer(required=True)})
    @jwt_required()
    def post(self, place_id):
        claims = get_jwt()
        current_user_id = claims.get('sub')

        data = api.payload

        if not data.get('text') or not data.get('rating'):
            return {'error': 'Text and rating are required'}, 400

        review_data = {
            'text': data['text'],
            'rating': int(data['rating']),
            'user_id': current_user_id,
            'place_id': place_id
        }

        try:
            review = HBnBFacade().create_review(review_data)

            review_response = {
                'id': str(review.id),
                'text': review.text,
                'rating': review.rating,
                'user_id': str(review.user_id),
                'user_name': "Utilisateur inconnu"
            }

            try:
                user = HBnBFacade().get_user(current_user_id)
                if user:
                    review_response['user_name'] = f"{user.first_name} {user.last_name}".strip()
            except:
                pass

            return review_response, 201
        except Exception as e:
            return {'error': str(e)}, 400
