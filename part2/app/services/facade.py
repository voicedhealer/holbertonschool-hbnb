from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity


class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ---------- USER ----------
    def create_user(self, user_data):
    # Vérifie que tous les champs requis sont présents
        if not user_data.get('first_name') or not user_data.get('last_name') or not user_data.get('email'):
            return {"message": "Missing required fields"}, 400

    # Vérifie que l'email n'existe pas déjà
        existing = self.get_user_by_email(user_data['email'])
        if existing:
            return {"message": "Email already exists"},  400

    # Crée l'utilisateur si tout est bon
        user = User(**user_data)
        user = self.user_repo.create(user)
        if hasattr(user, 'password'):
            user.password = None
        return user.__dict__


    def get_all_users(self):
        users = self.user_repo.get_all()
        return [{k: v for k, v in user.__dict__.items() if k != 'password'} for user in users]

    def get_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None:
            return None
        return {k: v for k, v in user.__dict__.items() if k != 'password'}

    def get_user_by_email(self, email):
        users = self.user_repo.get_all()
        for user in users:
            if getattr(user, 'email', None) == email:
                return user
        return None

    def list_users(self):
        users = self.user_repo.get_all()
        return [user.__dict__ for user in users]

    def update_user(self, user_id, update_data):
        user = self.user_repo.update(user_id, update_data)
        if user is None:
            return None
        return {k: v for k, v in user.__dict__.items() if k != 'password'}

    # ---------- PLACE ----------
    def create_place(self, place_data):
        place = Place(**place_data)
        return self.place_repo.create(place).__dict__

    def get_all_places(self):
        return [p.__dict__ for p in self.place_repo.get_all()]

    def get_place(self, place_id):
        place = self.place_repo.get(place_id)
        return place.__dict__ if place else None

    def update_place(self, place_id, update_data):
        place = self.place_repo.update(place_id, update_data)
        return place.__dict__ if place else None

    # ---------- REVIEW ----------
    def create_review(self, review_data):
        if not review_data.get('text'):
            raise ValueError("Review text is required")
        if not self.user_repo.get(review_data['user_id']):
            raise ValueError("User does not exist")
        if not self.place_repo.get(review_data['place_id']):
            raise ValueError("Place does not exist")
        review = Review(**review_data)
        return self.review_repo.create(review).__dict__

    def get_all_reviews(self):
        return [r.__dict__ for r in self.review_repo.get_all()]

    def get_review(self, review_id):
        review = self.review_repo.get(review_id)
        return review.__dict__ if review else None

    def update_review(self, review_id, update_data):
        review = self.review_repo.update(review_id, update_data)
        return review.__dict__ if review else None

    def delete_review(self, review_id):
        return self.review_repo.delete(review_id)

    # ---------- AMENITY ----------
    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        return self.amenity_repo.create(amenity).__dict__

    def get_all_amenities(self):
        return [a.__dict__ for a in self.amenity_repo.get_all()]

    def get_amenity(self, amenity_id):
        amenity = self.amenity_repo.get(amenity_id)
        return amenity.__dict__ if amenity else None

    def update_amenity(self, amenity_id, update_data):
        amenity = self.amenity_repo.update(amenity_id, update_data)
        return amenity.__dict__ if amenity else None