from typing import List, Dict, Optional, Any, Tuple, Union
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

    # ==========================
    # Opérations sur les Users
    # ==========================

    def create_user(self, user_data: Dict[str, Any]) -> Union[Tuple[Dict[str, Any], int], Dict[str, Any]]:
        if not all(user_data.get(key) for key in ['first_name', 'last_name', 'email']):
            return {"message": "Missing required fields"}, 400

        # Vérification de l'unicité de l'email
        if self.get_user_by_email(user_data['email']):
            return {"message": "Email already exists"}, 400

        # Création de l'utilisateur
        user = User(**user_data)
        created_user = self.user_repo.create(user)
        user_dict = dict(created_user.__dict__)
        user_dict.pop('password', None)
        return user_dict, 201

    def get_all_users(self) -> List[Dict[str, Any]]:
        users = self.user_repo.get_all()
        return [self._clean_user(user) for user in users]

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = self.user_repo.get(user_id)
        return self._clean_user(user) if user else None

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user = self.user_repo.update(user_id, update_data)
        return self._clean_user(user) if user else None

    def list_users(self):
        users = self.user_repo.get_all()
        return [self._clean_user(user) for user in users]

    def _clean_user(self, user: User) -> Dict[str, Any]:
        user_dict = dict(user.__dict__)
        user_dict.pop('password', None)
        return user_dict

    # ===========================
    # Opérations sur les Places
    # ===========================

    def create_place(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        place = Place(**place_data)
        return self.place_repo.create(place).__dict__

    def get_all_places(self) -> List[Dict[str, Any]]:
        return [p.__dict__ for p in self.place_repo.get_all()]

    def get_place(self, place_id: str) -> Optional[Dict[str, Any]]:
        place = self.place_repo.get(place_id)
        return place.__dict__ if place else None

    def update_place(self, place_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        place = self.place_repo.update(place_id, update_data)
        return place.__dict__ if place else None

    # ============================
    # Opérations sur les Reviews
    # ============================

    def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        if not review_data.get('text'):
            raise ValueError("Review text is required")
        if not self.user_repo.get(review_data['user_id']):
            raise ValueError("User does not exist")
        if not self.place_repo.get(review_data['place_id']):
            raise ValueError("Place does not exist")

        review = Review(**review_data)
        return self.review_repo.create(review).__dict__

    def get_all_reviews(self) -> List[Dict[str, Any]]:
        return [r.__dict__ for r in self.review_repo.get_all()]

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        review = self.review_repo.get(review_id)
        return review.__dict__ if review else None

    def update_review(self, review_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        review = self.review_repo.update(review_id, update_data)
        return review.__dict__ if review else None

    def delete_review(self, review_id: str) -> bool:
        return self.review_repo.delete(review_id)

    # =============================
    # Opérations sur les Amenities
    # =============================

    def create_amenity(self, amenity_data: Dict[str, Any]) -> Dict[str, Any]:
        amenity = Amenity(**amenity_data)
        created = self.amenity_repo.create(amenity)
        return created.to_dict()

    def get_all_amenities(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self.amenity_repo.get_all()]

    def get_amenity(self, amenity_id: str) -> Optional[Dict[str, Any]]:
        amenity = self.amenity_repo.get(amenity_id)
        return amenity.to_dict() if amenity else None

    def update_amenity(self, amenity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        amenity = self.amenity_repo.update(amenity_id, update_data)
        return amenity.to_dict() if amenity else None
