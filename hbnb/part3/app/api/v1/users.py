import re
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace('users', description='User operations')

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

# ------ Modèles Swagger ------
user_register_model = api.model('Register', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'username': fields.String(required=True),
    'password': fields.String(required=True, description="Mot de passe"),
    'role': fields.String(
        required=True,
        description="Rôle utilisateur ('owner' ou 'voyageur')",
        enum=['owner', 'voyageur']
    )
})

user_output_model = api.model('UserOut', {
    'id': fields.String(),
    'first_name': fields.String(),
    'last_name': fields.String(),
    'email': fields.String(),
    'username': fields.String(),
    'role': fields.String(),
    'profile_picture': fields.String()
})

def user_to_dict(user):
    return {
        'id': str(user.id),
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'username': getattr(user, 'username', None),
        'role': getattr(user, 'role', None),
        'profile_picture': getattr(user, 'profile_picture', None)
    }

# --------- ROUTE INSCRIPTION -----------
@api.route('/register')
class UserRegister(Resource):
    @api.expect(user_register_model, validate=True)
    @api.response(201, 'User created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Inscription libre (voyageur ou propriétaire)"""
        data = api.payload

        facade = HBnBFacade()

        if not EMAIL_REGEX.match(data['email']):
            return {'error': 'Invalid email format'}, 400

        if facade.get_user_by_email(data['email']):
            return {'error': 'Email already registered'}, 400

        if facade.get_user(data['username']):
            return {'error': 'Username already registered'}, 400

        if data.get('role') not in ("owner", "voyageur"):
            return {'error': 'Role must be owner or voyageur'}, 400

        try:
            user = facade.create_user(data)
            return user_to_dict(user), 201
        except Exception as e:
            return {'error': str(e)}, 400

# --------- ROUTE GET LIST ----------
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

# --------- ROUTE GET/PUT par ID (admin ou owner) ----------
@api.route('/<string:user_id>')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_output_model)
    @jwt_required()
    def get(self, user_id):
        user = HBnBFacade().get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user_to_dict(user), 200

    @api.doc('update_user')
    @api.expect(user_register_model, validate=True)
    @api.marshal_with(user_output_model)
    @jwt_required()
    def put(self, user_id):
        claims = get_jwt()
        current_user_id = claims.get('sub')
        is_admin = claims.get('is_admin', False)
        if not (is_admin or current_user_id == user_id):
            api.abort(403, "Permission denied")
        data = api.payload

        email = data.get('email')
        if email and not EMAIL_REGEX.match(email):
            api.abort(400, "Invalid email format")

        try:
            user = HBnBFacade().update_user(user_id, data)
            if not user:
                api.abort(404, 'User not found')
            return user_to_dict(user), 200
        except Exception as e:
            api.abort(400, str(e))
