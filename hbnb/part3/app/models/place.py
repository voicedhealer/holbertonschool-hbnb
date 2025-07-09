from .basemodel import BaseModel
from .user import User
from app import db

from .basemodel import BaseModel
from .user import User
from app import db

class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    # owner_id = db.Column(db.Integer, db.ForeignKey('app_users.id'), nullable=False)  # à activer plus tard

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            # 'owner_id': self.owner_id, # à activer plus tard
        }

    def __repr__(self):
        return f'<Place {self.title}>'
    @property
    def title(self):
        return self.__title
    
    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Title cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        BaseModel.is_max_length(self, 'title', value, 100)
        self.__title = value

    @property
    def price(self):
        return self.__price
    
    @price.setter
    def price(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Price must be a float")
        if value < 0:
            raise ValueError("Price must be positive.")
        self.__price = value

    @property
    def latitude(self):
        return self.__latitude
    
    @latitude.setter
    def latitude(self, value):
        if not isinstance(value, float):
            raise TypeError("Latitude must be a float")
        super().is_between("latitude", value, -90, 90)
        self.__latitude = value
    
    @property
    def longitude(self):
        return self.__longitude
    
    @longitude.setter
    def longitude(self, value):
        if not isinstance(value, float):
            raise TypeError("Longitude must be a float")
        super().is_between("longitude", value, -180, 180)
        self.__longitude = value

    @property
    def owner(self):
        return self.__owner
    
    @owner.setter
    def owner(self, value):
        if not isinstance(value, User):
            raise TypeError("Owner must be a user instance")
        self.__owner = value

    def add_review(self, review):
        """Ajouter un avis sur le lieu"""
        self.reviews.append(review)
    
    def delete_review(self, review):
        """Ajouter un agrément au lieu"""
        self.reviews.remove(review)

    def add_amenity(self, amenity):
        """Ajouter un agrément au lieu"""
        self.amenities.append(amenity)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner.id
        }
    
    def to_dict_list(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict(),
            'amenities': self.amenities,
            'reviews': self.reviews
        }

    @property
    def title(self):
        return self.__title
    
    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Title cannot be empty")
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        BaseModel.is_max_length(self, 'title', value, 100)
        self.__title = value

    @property
    def price(self):
        return self.__price
    
    @price.setter
    def price(self, value):
        if not isinstance(value, float) and not isinstance(value, int):
            raise TypeError("Price must be a float")
        if value < 0:
            raise ValueError("Price must be positive.")
        self.__price = value

    @property
    def latitude(self):
        return self.__latitude
    
    @latitude.setter
    def latitude(self, value):
        if not isinstance(value, float):
            raise TypeError("Latitude must be a float")
        super().is_between("latitude", value, -90, 90)
        self.__latitude = value
    
    @property
    def longitude(self):
        return self.__longitude
    
    @longitude.setter
    def longitude(self, value):
        if not isinstance(value, float):
            raise TypeError("Longitude must be a float")
        super().is_between("longitude", value, -180, 180)
        self.__longitude = value

    @property
    def owner(self):
        return self.__owner
    
    @owner.setter
    def owner(self, value):
        if not isinstance(value, User):
            raise TypeError("Owner must be a user instance")
        self.__owner = value

    def add_review(self, review):
        """Ajouter un avis sur le lieu"""
        self.reviews.append(review)
    
    def delete_review(self, review):
        """Ajouter un agrément au lieu"""
        self.reviews.remove(review)

    def add_amenity(self, amenity):
        """Ajouter un agrément au lieu"""
        self.amenities.append(amenity)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner.id
        }
    
    def to_dict_list(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict(),
            'amenities': self.amenities,
            'reviews': self.reviews
        }
