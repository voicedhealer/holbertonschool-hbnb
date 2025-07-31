from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity


api = Namespace('places', description='Place operations')
facade = HBnBFacade()


# Modèles Swagger / validation
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
    @api.response(403, 'Only owners can create a place')
    @jwt_required()
    def post(self):
         # ✅ TEST IMMÉDIAT - Ajoutez ces lignes en premier
        print("🚨 ENDPOINT POST /places/ APPELÉ")
        print("🚨 TEST DE DEBUG ACTIF")
        
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        print(f"🚨 USER ID: {current_user_id}")
        print(f"🚨 CLAIMS: {claims}")
        
        # ✅ Récupération correcte des informations JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        current_user_role = claims.get('role', 'voyageur')
        
        # ✅ DEBUG complet pour traquer le problème
        print(f"=== DEBUG CREATE PLACE ===")
        print(f"User ID from JWT: {current_user_id}")
        print(f"Claims complets: {claims}")
        print(f"Role dans claims: '{current_user_role}'")
        print(f"Type du rôle: {type(current_user_role)}")
        print(f"Est owner? {current_user_role == 'owner'}")
        print("========================")

        # ✅ Vérification du rôle propriétaire avec debug
        if current_user_role != "owner":
            error_msg = f'Forbidden: only owners can create places. Current role: {current_user_role}'
            print(f"❌ {error_msg}")
            return {'error': error_msg}, 403

        print(f"✅ Accès autorisé - Utilisateur propriétaire confirmé")

        # ✅ Validation des données
        data = api.payload.copy()
        data['owner_id'] = current_user_id

        # ✅ Vérification unicité de localisation
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Vérifier si la méthode existe avant de l'utiliser
        if hasattr(facade, 'find_place_by_location'):
            existing_place = facade.find_place_by_location(latitude, longitude)
            if existing_place:
                return {'error': 'A place already exists at this location'}, 400

        try:
            print(f"🔧 Tentative de création avec données: {data}")
            place = facade.create_place(data)
            print(f"✅ Place créée avec succès: {place.to_dict() if hasattr(place, 'to_dict') else place}")
            return place_to_dict(place, details=False), 201
        except Exception as e:
            print(f"❌ Erreur création place: {str(e)}")
            return {'error': str(e)}, 400

    def get(self):
        """Récupérer toutes les places"""
        try:
            places = facade.get_all_places()
            return [place_to_dict(p) for p in places], 200
        except Exception as e:
            print(f"❌ Erreur récupération places: {str(e)}")
            return {'error': 'Internal server error'}, 500

@api.route('/<place_id>')
class PlaceResource(Resource):
    @api.marshal_with(place_output_model)
    def get(self, place_id):
        """Récupérer une place par ID"""
        try:
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404
            return place_to_dict(place), 200
        except Exception as e:
            print(f"❌ Erreur récupération place {place_id}: {str(e)}")
            return {'error': 'Internal server error'}, 500

    @api.expect(place_model, validate=True)
    @jwt_required()
    def put(self, place_id):
        """Modifier une place"""
        # ✅ Récupération correcte des informations JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        current_user_role = claims.get('role', 'voyageur')

        print(f"=== DEBUG UPDATE PLACE ===")
        print(f"User ID: {current_user_id}")
        print(f"Role: {current_user_role}")
        print(f"Is admin: {is_admin}")
        print("========================")

        try:
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404

            # ✅ Vérification des permissions
            place_owner_id = str(place.owner_id) if hasattr(place, 'owner_id') else str(place.owner.id)
            
            if not (is_admin or (current_user_role == "owner" and str(current_user_id) == place_owner_id)):
                return {'error': 'Permission denied: only the owner or an admin can edit this place'}, 403

            data = api.payload
            new_lat = data.get('latitude', place.latitude)
            new_lon = data.get('longitude', place.longitude)
            
            # Vérification unicité nouvelle localisation
            if (new_lat != place.latitude or new_lon != place.longitude):
                if hasattr(facade, 'find_place_by_location'):
                    exist = facade.find_place_by_location(new_lat, new_lon)
                    if exist and str(exist.id) != str(place.id):
                        return {'error': 'Another place already exists at the new location'}, 400

            updated_place = facade.update_place(place_id, data)
            if not updated_place:
                return {'error': 'Place not found'}, 404
                
            return place_to_dict(updated_place), 200
            
        except Exception as e:
            print(f"❌ Erreur update place: {str(e)}")
            return {'error': str(e)}, 400

    @jwt_required()
    @api.response(200, 'Place deleted successfully')
    @api.response(404, 'Place not found')
    @api.response(403, 'Unauthorized')
    def delete(self, place_id):
        """Supprimer une place (propriétaire seulement)"""
        # ✅ Récupération correcte des informations JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        current_user_role = claims.get('role', 'voyageur')
        is_admin = claims.get('is_admin', False)

        print(f"=== DEBUG DELETE PLACE ===")
        print(f"User ID: {current_user_id}")
        print(f"Role: {current_user_role}")
        print(f"Is admin: {is_admin}")
        print("========================")

        try:
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404

            # ✅ Vérification des permissions
            place_owner_id = str(place.owner_id) if hasattr(place, 'owner_id') else str(place.owner.id)
            
            if not (is_admin or (current_user_role == "owner" and str(current_user_id) == place_owner_id)):
                return {'error': 'Unauthorized - Only owners or admin can delete this place'}, 403

            facade.delete_place(place_id)
            return {'message': 'Place deleted successfully'}, 200
            
        except Exception as e:
            print(f"❌ Erreur delete place: {str(e)}")
            return {'error': str(e)}, 500

@api.route('/<place_id>/amenities')
class PlaceAmenities(Resource):
    @api.expect(amenity_model)
    @api.response(200, 'Amenities added successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    @jwt_required()
    def post(self, place_id):
        """Ajouter des amenities à une place"""
        # ✅ Récupération correcte des informations JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        current_user_role = claims.get('role', 'voyageur')

        try:
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404
                
            # ✅ Vérification que l'utilisateur est propriétaire de cette place
            place_owner_id = str(place.owner_id) if hasattr(place, 'owner_id') else str(place.owner.id)
            
            if not (current_user_role == "owner" and str(current_user_id) == place_owner_id):
                return {'error': "Forbidden: only the owner can add amenities"}, 403

            amenities_data = api.payload
            if not amenities_data or len(amenities_data) == 0:
                return {'error': 'Invalid input data'}, 400

            # Validation des amenities
            for amenity in amenities_data:
                a = facade.get_amenity(amenity['id'])
                if not a:
                    return {'error': f"Amenity {amenity['id']} not found"}, 400

            # Ajout des amenities
            for amenity in amenities_data:
                if hasattr(place, 'add_amenity'):
                    place.add_amenity(amenity)
                    
            return {'message': 'Amenities added successfully'}, 200
            
        except Exception as e:
            print(f"❌ Erreur ajout amenities: {str(e)}")
            return {'error': str(e)}, 400

@api.route('/<place_id>/reviews/')
class PlaceReviewsList(Resource):
    def get(self, place_id):
        """Récupérer toutes les reviews d'une place"""
        try:
            reviews = facade.get_reviews_by_place(place_id)
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
                        user = facade.get_user(str(review.user_id))
                        if user:
                            review_data['user_name'] = f"{user.first_name} {user.last_name}".strip()
                    except:
                        pass
                        
                formatted_reviews.append(review_data)

            return formatted_reviews, 200
            
        except Exception as e:
            print(f"❌ Erreur récupération reviews: {str(e)}")
            return {'error': 'Internal server error'}, 500

    @api.expect({'text': fields.String(required=True), 'rating': fields.Integer(required=True)})
    @jwt_required()
    def post(self, place_id):
        """Créer une nouvelle review"""
        # ✅ Récupération correcte des informations JWT
        current_user_id = get_jwt_identity()
        claims = get_jwt()

        try:
            data = api.payload

            if not data.get('text') or not data.get('rating'):
                return {'error': 'Text and rating are required'}, 400

            # Validation du rating
            rating = int(data['rating'])
            if rating < 1 or rating > 5:
                return {'error': 'Rating must be between 1 and 5'}, 400

            review_data = {
                'text': data['text'],
                'rating': rating,
                'user_id': current_user_id,
                'place_id': place_id
            }

            review = facade.create_review(review_data)
            
            review_response = {
                'id': str(review.id),
                'text': review.text,
                'rating': review.rating,
                'user_id': str(review.user_id),
                'user_name': "Utilisateur inconnu"
            }
            
            try:
                user = facade.get_user(current_user_id)
                if user:
                    review_response['user_name'] = f"{user.first_name} {user.last_name}".strip()
            except:
                pass

            return review_response, 201
            
        except Exception as e:
            print(f"❌ Erreur création review: {str(e)}")
            return {'error': str(e)}, 400
