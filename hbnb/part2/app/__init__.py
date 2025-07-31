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

    # 1. Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # 2. Import namespaces API localement pour éviter les circular imports
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns

    # Optionnel : gestion CORS si besoin front séparé
    # from flask_cors import CORS
    # CORS(app)

    authorizations = {
        'jwt': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Entrez 'Bearer <token>' pour l'authentification."
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

    # 3. Ajout namespaces (vérifie bien que chaque namespace a un path déclaré, si non, ajoute-le ici)
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    # 4. Commande CLI pour initialiser la base
    @app.cli.command("init-db")
    def init_db_command():
        """Crée toutes les tables de la base de données."""
        with app.app_context():
            from app.models.user import User
            from app.models.place import Place
            from app.models.review import Review
            from app.models.amenity import Amenity
            print("Création des tables...")
            db.create_all()
            print("Base de données initialisée avec succès.")

    return app
