from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('users', description='User operations')

user_input_model = api.model('UserInput', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True, description="Password (only for creation)")
})

user_output_model = api.model('UserOut', {
    'id': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String()
})

def user_to_dict(user):
    return {
        'id': str(user.id),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }

@api.route('/')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(user_output_model)
    @jwt_required()
    def get(self):
        """List all users (admin only)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            api.abort(403, 'Admin only')
        users = HBnBFacade().get_all_users()
        return [user_to_dict(u) for u in users]

    @api.doc('create_user')
    @api.expect(user_input_model, validate=True)
    @api.response(201, 'User created', user_output_model)
    @api.response(400, 'Invalid input')
    def post(self):
        """Create a new user"""
        data = api.payload
        try:
            user = HBnBFacade().create_user(data)
            return user_to_dict(user), 201
        except Exception as e:
            return {'error': str(e)}, 400

@api.route('/<string:user_id>')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_output_model)
    @jwt_required()
    def get(self, user_id):
        """Get a user by ID"""
        user = HBnBFacade().get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user_to_dict(user), 200

    @api.doc('update_user')
    @api.expect(user_input_model, validate=True)
    @api.marshal_with(user_output_model)
    @jwt_required()
    def put(self, user_id):
        """Update a user"""
        data = api.payload
        try:
            user = HBnBFacade().update_user(user_id, data)
            if not user:
                api.abort(404, 'User not found')
            return user_to_dict(user), 200
        except Exception as e:
            api.abort(400, str(e))
