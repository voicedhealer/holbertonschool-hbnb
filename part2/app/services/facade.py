from typing import List, Optional, TYPE_CHECKING
from app.models.base import BaseModel
from app.persistence.repository import Repository

# Pour éviter les importations circulaires tout en gardant le type hinting
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.review import Review
    from app.models.amenity import Amenity

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
        repo = UserRepository()
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
