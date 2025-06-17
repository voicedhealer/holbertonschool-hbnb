from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ---------- USER ----------
    def create_user(self, user_data):
        user = self.user_repo.create(user_data)
        if 'password' in user:
            user = dict(user)
            user.pop('password')
        return user

    def get_all_users(self):
        users = self.user_repo.get_all()
        return [{k: v for k, v in user.items() if k != 'password'} for user in users]

    def get_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None:
            return None
        return {k: v for k, v in user.items() if k != 'password'}

    def get_user_by_email(self, email):
        users = self.user_repo.get_all()
        for user in users:
            if getattr(user, 'email', None) == email:
                return user
        return None

    def update_user(self, user_id, update_data):
        user = self.user_repo.update(user_id, update_data)
        if user is None:
            return None
        return {k: v for k, v in user.items() if k != 'password'}

    # ---------- PLACE ----------
    def create_place(self, place_data):
        return self.place_repo.create(place_data)

    def get_all_places(self):
        return self.place_repo.get_all()

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def update_place(self, place_id, update_data):
        return self.place_repo.update(place_id, update_data)

    # ---------- REVIEW ----------
    def create_review(self, review_data):
        return self.review_repo.create(review_data)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def update_review(self, review_id, update_data):
        return self.review_repo.update(review_id, update_data)

    # ---------- AMENITY ----------
    def create_amenity(self, amenity_data):
        return self.amenity_repo.create(amenity_data)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def update_amenity(self, amenity_id, update_data):
        return self.amenity_repo.update(amenity_id, update_data)
