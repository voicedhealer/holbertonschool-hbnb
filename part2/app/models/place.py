from app.models.base import BaseModel

class Place(BaseModel):
    """
    class Place 
    """
    def __init__(self, title, description, city, price, latitude, longitude, name, owner, reviews=None, address=None):
        super().__init__()
        self.title = title
        self.description = description
        self.city = city
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.name = name
        self.owner = owner
        self.reviews = reviews if reviews is not None else []
        self.address =  address
        self.amenities = []

    def add_review(self, review):
        """Add a review to the place."""
        self.reviews.append(review)

    def add_amenity(self, amenity):
        """Add an amenity to the place."""
        self.amenities.append(amenity)