from app.models.user import User
from app.models.review import Review
from app.models.amenity import Amenity
from app.models.place import Place

from app.persistence.repository import SQLAlchemyRepository
from app.persistence.user_repository import UserRepository

user_repo = UserRepository()

class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)

    # --- USER ---
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

    # --- AMENITY ---
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

    # --- PLACE ---
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
                place.amenities.append(amenity)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)

    # --- REVIEW ---
    def create_review(self, review_data):
        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def update_review(self, review_id, review_data):
        self.review_repo.update(review_id, review_data)
