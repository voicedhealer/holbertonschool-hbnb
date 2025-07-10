from flask_restx import Namespace, Resource, fields
from app.services.auth import login_user  # ← appel au service
from flask_jwt_extended import create_access_token
from app.services.facade import HBnBFacade

api = Namespace('auth', description='Auth operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description="User email"),
    'password': fields.String(required=True, description="User password")
})

token_model = api.model('Token', {
    'access_token': fields.String(description="JWT access token")
})

error_model = api.model('Error', {
    'error': fields.String()
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model, validate=True)
    @api.marshal_with(token_model)
    @api.response(200, 'Success', token_model)
    @api.response(401, 'Invalid credentials', error_model)
    def post(self):
        data = api.payload
        data = api.payload
        user = HBnBFacade().get_user_by_email(data['email'])
        if not user or not user.check_password(data['password']):
            api.abort(401, "Invalid credentials")
        token = create_access_token(identity=str(user.id))
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'error': 'Email and password are required'}, 400
        token = login_user(email, password)
        if not token:
            return {'error': 'Invalid credentials'}, 401
        return {'access_token': token}, 200
