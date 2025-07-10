from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required

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
    'place_id': fields.String()
})

def review_to_dict(review):
    return {
        'id': review.id,
        'text': review.text,
        'rating': review.rating,
        'user_id': review.user_id,
        'place_id': review.place_id
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

    @api.marshal_list_with(review_output_model)
    def get(self):
        reviews = HBnBFacade().get_all_reviews()
        return [review_to_dict(r) for r in reviews], 200

@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.marshal_with(review_output_model)
    def get(self, review_id):
        review = HBnBFacade().get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review_to_dict(review), 200

    @api.expect(review_model, validate=True)
    @jwt_required()
    def put(self, review_id):
        data = api.payload
        try:
            review = HBnBFacade().update_review(review_id, data)
        except Exception as e:
            return {'error': str(e)}, 400
        if not review:
            return {'error': 'Review not found'}, 404
        return review_to_dict(review), 200

    @jwt_required()
    def delete(self, review_id):
        deleted = HBnBFacade().delete_review(review_id)
        if not deleted:
            return {'error': 'Review not found'}, 404
        return {'message': 'Review deleted successfully'}, 200

@api.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @api.marshal_list_with(review_output_model)
    def get(self, place_id):
        reviews = HBnBFacade().get_reviews_by_place(place_id)
        if reviews is None:
            return {'error': 'Place not found'}, 404
        return [review_to_dict(r) for r in reviews], 200
