from flask import Flask
from flask_restx import Api
from app.api.v1.users import api as user_ns
from app.api.v1.amenities import amenity_ns
from app.api.v1.places import place_ns
from app.api.v1.reviews import reviews_ns

def create_app():
    app = Flask(__name__)
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/'
    )
    api.add_namespace(user_ns, path='/api/v1/users')
    api.add_namespace(amenity_ns, path='/api/v1/amenities')
    api.add_namespace(place_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    return app
