from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True),
    'rating': fields.Integer(required=True),
    'user_id': fields.String(required=True),
    'place_id': fields.String(required=True)
})

review_output_model = api.model('ReviewOut', {
    'id': fields.String(),
    'text': fields.String(),
    'rating': fields.Integer(),
    'user_id': fields.String(),
    'user_name': fields.String(),
    'place_id': fields.String()
})

def review_to_dict(review):
    # Récupération du nom d'utilisateur
    user_name = "Utilisateur inconnu"
    if hasattr(review, 'user') and review.user:
        user_name = f"{review.user.first_name} {review.user.last_name}".strip()
    elif hasattr(review, 'user_id'):
        # Si pas de relation directe, essaie de récupérer via facade
        try:
            user = HBnBFacade().get_user(str(review.user_id))
            if user:
                user_name = f"{user.first_name} {user.last_name}".strip()
        except:
            pass
    
    return {
        'id': str(review.id),
        'text': review.text,
        'rating': review.rating,
        'user_id': str(review.user_id),
        'user_name': user_name,
        'place_id': str(review.place_id)
    }

@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review created')
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self):
        data = api.payload
        try:
            review = HBnBFacade().create_review(data)
        except Exception as e:
            return {'error': str(e)}, 400
        return review_to_dict(review), 201

    def get(self):
        reviews = HBnBFacade().get_all_reviews()
        return [review_to_dict(r) for r in reviews], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    def get(self, review_id):
        review = HBnBFacade().get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review_to_dict(review), 200

    @api.expect(review_model, validate=True)
    @api.response(403, "Permission denied")
    @jwt_required()
    def put(self, review_id):
        claims = get_jwt()
        current_user_id = claims.get('sub')
        is_admin = claims.get('is_admin', False)
        review = HBnBFacade().get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not (is_admin or str(review.user_id) == current_user_id):
            return {'error': 'Permission denied'}, 403
        data = api.payload
        try:
            updated = HBnBFacade().update_review(review_id, data)
        except Exception as e:
            return {'error': str(e)}, 400
        if not updated:
            return {'error': 'Review not found'}, 404
        return review_to_dict(updated), 200

    @api.response(403, "Permission denied")
    @jwt_required()
    def delete(self, review_id):
        claims = get_jwt()
        current_user_id = claims.get('sub')
        is_admin = claims.get('is_admin', False)
        review = HBnBFacade().get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        if not (is_admin or str(review.user_id) == current_user_id):
            return {'error': 'Permission denied'}, 403
        deleted = HBnBFacade().delete_review(review_id)
        if not deleted:
            return {'error': 'Review not found'}, 404
        return {'message': 'Review deleted successfully'}, 200

@api.route('/places/<place_id>/reviews/')
class PlaceReviewList(Resource):
    def get(self, place_id):
        reviews = HBnBFacade().get_reviews_by_place(place_id)
        if reviews is None:
            return {'error': 'Place not found'}, 404
        return [review_to_dict(r) for r in reviews], 200
    
    @api.expect({'text': fields.String(required=True), 'rating': fields.Integer(required=True)})
    @api.response(201, 'Review created')
    @api.response(400, 'Invalid input')
    @jwt_required()
    def post(self, place_id):
        """Créer un avis pour un lieu spécifique"""
        claims = get_jwt()
        current_user_id = claims.get('sub')
        
        data = api.payload
        
        # Ajout automatique des IDs
        review_data = {
            'text': data['text'],
            'rating': data['rating'],
            'user_id': current_user_id,
            'place_id': place_id
        }
        
        try:
            review = HBnBFacade().create_review(review_data)
        except Exception as e:
            return {'error': str(e)}, 400
        return review_to_dict(review), 201
