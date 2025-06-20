"""
Module définissant le modèle de données pour un 'Place'.
"""
from typing import List, Optional, TYPE_CHECKING

from app.models.base import BaseModel

# Pour éviter les importations circulaires tout en gardant le type hinting
if TYPE_CHECKING:
    from app.models.user import User
    from app.models.review import Review
    from app.models.amenity import Amenity


class Place(BaseModel):
    """
    Représente un lieu ou un logement disponible dans l'application.

    Cette classe est une entité centrale qui contient toutes les informations
    relatives à une propriété spécifique. Elle hérite de `BaseModel` pour les
    attributs communs comme `id`, `created_at`, et `updated_at`.

    Attributes:
        title (str): Le titre public du lieu (ex: "Appartement cosy avec vue").
        description (str): Une description détaillée du lieu.
        city (str): La ville où se trouve le lieu.
        price (float): Le prix par nuit.
        latitude (float): La coordonnée de latitude géographique.
        longitude (float): La coordonnée de longitude géographique.
        name (str): Un nom spécifique pour le lieu, potentiellement pour un usage interne.
        owner (User): L'objet utilisateur qui est propriétaire de ce lieu.
        reviews (List[Review]): Une liste des objets Review associés à ce lieu.
        address (Optional[str]): L'adresse complète et facultative du lieu.
        amenities (List[Amenity]): Une liste des objets Amenity disponibles dans ce lieu.
    """
    def __init__(self, title: str, description: str, city: str, price: float,
                 latitude: float, longitude: float, name: str, owner: 'User',
                 reviews: Optional[List['Review']] = None, address: Optional[str] = None):
        """
        Initialise une nouvelle instance de Place.

        Args:
            title (str): Le titre public du lieu.
            description (str): La description détaillée.
            city (str): La ville de localisation.
            price (float): Le prix par nuit.
            latitude (float): La latitude du lieu.
            longitude (float): La longitude du lieu.
            name (str): Le nom spécifique du lieu.
            owner (User): L'instance de l'utilisateur propriétaire.
            reviews (Optional[List[Review]]): Liste initiale facultative de reviews.
            address (Optional[str]): Adresse complète facultative.
        """
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
        self.address = address
        self.amenities: List['Amenity'] = []

    def add_review(self, review: 'Review') -> None:
        """
        Ajoute un objet Review à la liste des reviews du lieu.

        Args:
            review (Review): L'instance de Review à ajouter.
        """
        self.reviews.append(review)

    def add_amenity(self, amenity: 'Amenity') -> None:
        """
        Associe une Amenity à ce lieu.

        Args:
            amenity (Amenity): L'instance d'Amenity à ajouter à la liste.
        """
        self.amenities.append(amenity)
