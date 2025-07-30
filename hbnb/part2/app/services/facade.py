from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)

    # ---------- USER ----------
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

    # ---------- AMENITY ----------
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

    # ---------- PLACE ----------
    def create_place(self, place_data):
        # 1. Vérification owner
        owner = self.user_repo.get_by_attribute('id', place_data['owner_id'])
        if not owner:
            raise KeyError('Invalid owner_id')
        
        # 2. Amenities: charger les objets
        amenities = []
        amenities_ids = place_data.pop('amenities', [])  # Liste d'ID d'amenities
        for am_id in amenities_ids:
            amenity = self.get_amenity(am_id)
            if not amenity:
                raise KeyError(f'Invalid amenity id: {am_id}')
            amenities.append(amenity)

        # 3. Création de la Place (sans owner_id mais owner object, normalisé)
        place_data['owner'] = owner
        place = Place(**place_data)
        self.place_repo.add(place)
        
        # 4. Ajout amenities à la place (si méthode appropriée)
        for amenity in amenities:
            place.add_amenity(amenity)
        
        # 5. Ajout place à l'owner si logique
        if hasattr(owner, "add_place"):
            owner.add_place(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)

    def delete_place(self, place_id):
        place = self.get_place(place_id)
        if not place:
            raise ValueError("Place not found")
        # Détacher des owner/amenity/review si logique d'ORM le requiert (cascade ?)
        owner = place.owner
        if hasattr(owner, "remove_place"):
            owner.remove_place(place)
        # Suppression directe
        self.place_repo.delete(place_id)

    # ---------- REVIEW ----------
    def create_review(self, review_data):
        user = self.user_repo.get_by_attribute('id', review_data['user_id'])
        if not user:
            raise KeyError('Invalid user_id')
        place = self.place_repo.get_by_attribute('id', review_data['place_id'])
        if not place:
            raise KeyError('Invalid place_id')
        review_data['user'] = user
        review_data['place'] = place
        review = Review(**review_data)
        self.review_repo.add(review)
        if hasattr(user, "add_review"):
            user.add_review(review)
        if hasattr(place, "add_review"):
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
        return getattr(place, "reviews", [])

    def update_review(self, review_id, review_data):
        self.review_repo.update(review_id, review_data)

    def delete_review(self, review_id):
        review = self.review_repo.get(review_id)
        if not review:
            raise ValueError('Review not found')
        user = review.user
        place = review.place
        if hasattr(user, "remove_review"):
            user.remove_review(review)
        if hasattr(place, "remove_review"):
            place.remove_review(review)
        self.review_repo.delete(review_id)
