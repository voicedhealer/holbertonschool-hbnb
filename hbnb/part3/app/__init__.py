from flask import Flask
from flask_restx import Api
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app(config_class="app.config.DevelopmentConfig"):
    """
    Factory pour créer et configurer l'instance de l'application Flask.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["JWT_SECRET_KEY"] = "votre_cle_secrete"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # Initialisation des extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Importation et enregistrement des blueprints/namespaces
    from .api.v1.users import users_bp
    from app.api.v1.users import users_bp
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.users import api as users_api
    from app.api.v1.auth import api as auth_ns

    app.register_blueprint(users_bp, url_prefix='/api/v1/users')

    authorizations = {
        'jwt': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': (
                "Entrez 'Bearer <token>' pour l'authentification. "
                "Exemple: 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'"
            )
        }
    }

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        authorizations=authorizations,
        security='jwt'
    )
    api.add_namespace(users_api, path='/api/v1/users')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    api.add_namespace(users_ns)
    api.add_namespace(amenities_ns)
    api.add_namespace(places_ns)
    api.add_namespace(reviews_ns)

    @app.cli.command("init-db")
    def init_db_command():
        """Crée toutes les tables de la base de données et l’admin par défaut."""
        with app.app_context():
            from app.models.user import User
            db.create_all()
            # Création de l’admin par défaut
            if not User.query.filter_by(role='admin').first():
                admin = User(
                username='admin',
                email='admin@hbnb.com',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                role='admin'
            )
                admin.hash_password('Hbnb2025*-')
                db.session.add(admin)
                db.session.commit()
                print("Admin par défaut créé.")
            else:
                print("Un admin existe déjà.")

    return app
