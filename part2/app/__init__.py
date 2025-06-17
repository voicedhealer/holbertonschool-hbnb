from flask import Flask
from flask_restx import Api
from api.v1.amenities import amenity_ns

def create_app():
    app = Flask(__name__)
    api = Api(app)
    api.add_namespace(amenity_ns, path='/api/v1/amenities')
    # Ajoute ici d'autres namespaces si besoin
    return app
