from typing import List, Optional, TYPE_CHECKING
from app.models.basemodel import BaseModel
from app.persistence.repository import Repository
from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity
from app.models.place import Place

if TYPE_CHECKING:
    # (optionnel pour les IDE/type-checkers)
    pass

class Place(BaseModel):
    """
    Représente un lieu ou un logement disponible dans l'application.
    """

    def __init__(
        self,
        title: str,
        description: str,
        city: str,
        price: float,
        latitude: float,
        longitude: float,
        name: str,
        owner_id: str,
        reviews: Optional[List['Review']] = None,
        address: Optional[str] = None,
        amenities: Optional[List['Amenity']] = None
    ):
        super().__init__()
        self.title = title
        self.description = description
        self.city = city
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.address = address
        self.reviews = reviews if reviews is not None else []
        self.amenities = amenities if amenities is not None else []

        # Convertir owner_id → objet owner (User)
        repo = Repository()
        user_obj = repo.get(owner_id)
        if user_obj is None:
            raise ValueError(f"Aucun utilisateur trouvé avec l'ID {owner_id}")
        self.owner = user_obj

    def add_review(self, review: 'Review') -> None:
        self.reviews.append(review)

    def add_amenity(self, amenity: 'Amenity') -> None:
        self.amenities.append(amenity)

    def to_dict(self):
        """Retourne un dictionnaire représentant le lieu."""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'city': self.city,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'name': self.name,
            'owner_id': self.owner.id if self.owner else None,
            'address': self.address,
            'amenities': [a.id for a in self.amenities] if self.amenities else [],
        }


class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()

    def create_user(self, user_data):
        password = user_data.pop('password')
        user = User(**user_data)
        user.hash_password(password)
        self.user_repo.add(user)
        return user
    
    def get_users(self):
        return self.user_repo.get_all()

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)
    
    def update_user(self, user_id, user_data):
        self.user_repo.update(user_id, user_data)
    
    # AMENITY
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        self.amenity_repo.update(amenity_id, amenity_data)

    # PLACE
    def create_place(self, place_data):
        user = self.user_repo.get(place_data['owner_id'])
        if not user:
            raise KeyError('Invalid input data')

        amenities = place_data.pop('amenities', None)
        place = Place(**place_data)
        self.place_repo.add(place)
        user.add_place(place)
        if amenities:
            for amenity in amenities:
                place.add_amenity(self.get_amenity(amenity['id']))
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)

    # REVIEWS
    def create_review(self, review_data):
        user = self.user_repo.get(review_data['user_id'])
        if not user:
            raise KeyError('Invalid input data')
        del review_data['user_id']
        review_data['user'] = user
        
        place = self.place_repo.get(review_data['place_id'])
        if not place:
            raise KeyError('Invalid input data')
        del review_data['place_id']
        review_data['place'] = place

        review = Review(**review_data)
        self.review_repo.add(review)
        user.add_review(review)
        place.add_review(review)
        return review
        
    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        place = self.place_repo.get(place_id)
        if not place:
            raise KeyError('Place not found')
        return place.reviews

    def update_review(self, review_id, review_data):
        self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        
        user = self.user_repo.get(review.user.id)
        place = self.place_repo.get(review.place.id)

        user.delete_review(review)
        place.delete_review(review)
        self.review_repo.delete(review_id)
