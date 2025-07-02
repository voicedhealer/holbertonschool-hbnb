from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

api = Namespace('auth', description='Authentication operations')

# Modèle de validation des entrées
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload  # Récupérez l'e-mail et le mot de passe à partir de la charge utile de la requête
        
        # Étape 1 : Récupérer l'utilisateur en fonction de l'e-mail fourni
        user = facade.get_user_by_email(credentials['email'])
        
        # Étape 2 : Vérifiez si l’utilisateur existe et si le mot de passe est correct
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Étape 3 : Créez un jeton JWT avec l'ID de l'utilisateur et l'indicateur is_admin
        access_token = create_access_token(identity={'id': str(user.id), 'is_admin': user.is_admin})
        
        # Étape 4 : renvoyer le jeton JWT au client
        return {'access_token': access_token}, 200
