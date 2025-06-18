from app.models.base import BaseModel
from datetime import datetime
from flask_restx import Namespace

place_ns = Namespace("places", description="Places operations")

class Place(BaseModel):
    def __init__(self, name, description, city, address, price, owner_id, **kwargs):
        """
        Constructeur de la classe Place.
        Initialise un lieu avec ses attributs principaux.
        """
        super().__init__()
        self.name = name  # Nom du lieu
        self.description = description  # Description du lieu
        self.city = city  # Ville
        self.address = address  # Adresse précise
        self.price = price  # Prix par nuit ou par séjour
        self.owner_id = owner_id  # ID du propriétaire (User)
        # Ajoute d'autres attributs spécifiques si besoin (nombre de chambres, etc.)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self, **kwargs):
        """
        Met à jour les attributs du lieu avec les valeurs fournies.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.updated_at = datetime.now()
