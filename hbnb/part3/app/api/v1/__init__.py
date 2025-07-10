from .users import api as users_ns
# from .places import api as places_ns
# from .reviews import api as reviews_ns
# from .amenities import api as amenities_ns
from .auth import api as auth_ns

def register_namespaces(api):
    api.add_namespace(users_ns, path='/api/v1/users')
    # api.add_namespace(places_ns, path='/api/v1/places')
    # api.add_namespace(reviews_ns, path='/api/v1/reviews')
    # api.add_namespace(amenities_ns, path='/api/v1/amenities')
    # api.add_namespace(auth_ns, path='/api/v1/auth')
