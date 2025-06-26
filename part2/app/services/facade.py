from typing import List, Dict, Optional, Any, Tuple, Union

from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from uuid import UUID


class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ==========================
    # Users
    # ==========================

    def create_user(self, user_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        if not all(user_data.get(key) for key in ['first_name', 'last_name', 'email']):
            return {"message": "Missing required fields"}, 400

        if self.get_user_by_email(user_data['email']):
            return {"message": "Email already exists"}, 400

        user = User(**user_data)
        created_user = self.user_repo.create(user)
        user_dict = dict(created_user.__dict__)
        user_dict.pop('password', None)
        return user_dict, 201

    def get_all_users(self) -> List[Dict[str, Any]]:
        users = self.user_repo.get_all()
        return [{k: v for k, v in user.__dict__.items() if k != 'password'} for user in users]

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        user = self.user_repo.get(user_id)
        if user is None:
            return None
        user_dict = dict(user.__dict__)
        user_dict.pop('password', None)
        return user_dict

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user = self.user_repo.update(user_id, update_data)
        if user is None:
            return None
        user_dict = dict(user.__dict__)
        user_dict.pop('password', None)
        return user_dict

    def list_users(self) -> List[Dict[str, Any]]:
        users = self.user_repo.get_all()
        return [user if isinstance(user, dict) else dict(user.__dict__) for user in users]

    # ==========================
    # Places
    # ==========================

    def create_place(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        place = Place(**place_data)
        return dict(self.place_repo.create(place).__dict__)

    def get_all_places(self) -> List[Dict[str, Any]]:
        return [dict(p.__dict__) for p in self.place_repo.get_all()]

    def get_place(self, place_id: str) -> Optional[Dict[str, Any]]:
        place = self.place_repo.get(place_id)
        return dict(place.__dict__) if place else None

    def update_place(self, place_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        place = self.place_repo.update(place_id, update_data)
        return dict(place.__dict__) if place else None

    # ============================
    # Reviews
    # ============================

    def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        if not review_data.get('text'):
            raise ValueError("Review text is required")
        if not self.user_repo.get(review_data['user_id']):
            raise ValueError("User does not exist")
        if not self.place_repo.get(review_data['place_id']):
            raise ValueError("Place does not exist")
        review = Review(**review_data)
        return dict(self.review_repo.create(review).__dict__)

    def get_all_reviews(self) -> List[Dict[str, Any]]:
        return [dict(r.__dict__) for r in self.review_repo.get_all()]

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        review = self.review_repo.get(review_id)
        return dict(review.__dict__) if review else None

    def update_review(self, review_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        review = self.review_repo.update(review_id, update_data)
        return dict(review.__dict__) if review else None

    def delete_review(self, review_id: str) -> bool:
        return self.review_repo.delete(review_id)

    # =============================
    # Amenities
    # =============================

    def create_amenity(self, amenity_data: Dict[str, Any]) -> Dict[str, Any]:
        amenity = Amenity(**amenity_data)
        return dict(self.amenity_repo.create(amenity).__dict__)

    def get_all_amenities(self) -> List[Dict[str, Any]]:
        return [dict(a.__dict__) for a in self.amenity_repo.get_all()]

    def get_amenity(self, amenity_id: str) -> Optional[Dict[str, Any]]:
        try:
            uuid = UUID(amenity_id)
            amenity = self.amenity_repo.get(str(uuid))
            return dict(amenity.__dict__) if amenity else None
        except ValueError:
            return None

    def update_amenity(self, amenity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        amenity = self.amenity_repo.update(amenity_id, update_data)
        return dict(amenity.__dict__) if amenity else None
