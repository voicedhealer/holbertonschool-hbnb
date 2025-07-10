from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.amenity_repository import AmenityRepository
from app.repositories.review_repository import ReviewRepository
from app.models.user import User
from app.models.place import Place, PlaceAmenity
from app.models.amenity import Amenity
from app.models.review import Review
from werkzeug.security import generate_password_hash

class HBnBFacade:
    # ---------- USER ----------
    def create_user(self, data):
        if hasattr(User, "validate_data"):
            User.validate_data(data)
        if User.query.filter_by(email=data['email']).first():
            raise ValueError("Email already registered")
        user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email']
        )
        if hasattr(user, "set_password"):
            user.set_password(data['password'])
        else:
            user.password_hash = generate_password_hash(data['password'])
        db.session.add(user)
        db.session.commit()
        return user

    def get_user(self, user_id):
        return db.session.get(User, user_id)

    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_all_users(self):
        return User.query.all()

    def update_user(self, user_id, data):
        user = self.get_user(user_id)
        if not user:
            return None
        if 'email' in data and data['email'] != user.email:
            if self.get_user_by_email(data['email']):
                raise ValueError("Email already registered")
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'password' in data:
            if hasattr(user, "set_password"):
                user.set_password(data['password'])
            else:
                user.password_hash = generate_password_hash(data['password'])
        db.session.commit()
        return user

    # ---------- AMENITY ----------
    def create_amenity(self, data):
        if not data.get('name') or len(data['name']) > 50:
            raise ValueError("Amenity name is required and must be <= 50 chars")
        amenity = Amenity(name=data['name'])
        db.session.add(amenity)
        db.session.commit()
        return amenity

    def get_amenity(self, amenity_id):
        return db.session.get(Amenity, amenity_id)

    def get_all_amenities(self):
        return Amenity.query.all()

    def update_amenity(self, amenity_id, data):
        amenity = self.get_amenity(amenity_id)
        if not amenity:
            return None
        if 'name' in data:
            if not data['name'] or len(data['name']) > 50:
                raise ValueError("Amenity name is required and must be <= 50 chars")
            amenity.name = data['name']
        db.session.commit()
        return amenity

    # ---------- PLACE ----------
    def create_place(self, data):
        owner = db.session.get(User, data['owner_id'])
        if not owner:
            raise ValueError("Owner not found")
        amenities = []
        for amenity_id in data.get('amenities', []):
            amenity = db.session.get(Amenity, amenity_id)
            if not amenity:
                raise ValueError(f"Amenity not found: {amenity_id}")
            amenities.append(amenity)
        place = Place(
            title=data['title'],
            description=data.get('description', ''),
            price=data['price'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            owner=owner
        )
        db.session.add(place)
        db.session.flush()  # Pour obtenir l'ID du place

        for amenity in amenities:
            pa = PlaceAmenity(place_id=place.id, amenity_id=amenity.id)
            db.session.add(pa)
        db.session.commit()
        return place

    def get_place(self, place_id):
        return db.session.get(Place, place_id)

    def get_all_places(self):
        return Place.query.all()

    def update_place(self, place_id, data):
        place = self.get_place(place_id)
        if not place:
            return None
        updatable = ['title', 'description', 'price', 'latitude', 'longitude']
        for key in updatable:
            if key in data:
                setattr(place, key, data[key])
        if 'owner_id' in data:
            owner = db.session.get(User, data['owner_id'])
            if not owner:
                raise ValueError("Owner not found")
            place.owner_id = owner.id
        if 'amenities' in data:
            PlaceAmenity.query.filter_by(place_id=place.id).delete()
            for amenity_id in data['amenities']:
                amenity = db.session.get(Amenity, amenity_id)
                if not amenity:
                    raise ValueError(f"Amenity not found: {amenity_id}")
                pa = PlaceAmenity(place_id=place.id, amenity_id=amenity.id)
                db.session.add(pa)
        db.session.commit()
        return place

    # ---------- REVIEW ----------
    def create_review(self, data):
        user_id = data['user_id']
        place_id = data['place_id']
        user = db.session.get(User, user_id)
        place = db.session.get(Place, place_id)
        if not user:
            raise ValueError("User not found")
        if not place:
            raise ValueError("Place not found")
        rating = data['rating']
        if not (1 <= int(rating) <= 5):
            raise ValueError("Rating must be between 1 and 5")
        review = Review(
            text=data['text'],
            rating=rating,
            place=place,
            user=user
        )
        db.session.add(review)
        db.session.commit()
        return review

    def get_review(self, review_id):
        return db.session.get(Review, review_id)

    def get_all_reviews(self):
        return Review.query.all()

    def get_reviews_by_place(self, place_id):
        place = db.session.get(Place, place_id)
        if not place:
            return None
        return place.reviews

    def update_review(self, review_id, data):
        review = self.get_review(review_id)
        if not review:
            return None
        if 'text' in data:
            review.text = data['text']
        if 'rating' in data:
            rating = data['rating']
            if not (1 <= int(rating) <= 5):
                raise ValueError("Rating must be between 1 and 5")
            review.rating = int(rating)
        db.session.commit()
        return review

    def delete_review(self, review_id):
        review = self.get_review(review_id)
        if not review:
            return False
        db.session.delete(review)
        db.session.commit()
        return True
