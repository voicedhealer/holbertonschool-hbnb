from app.models.base import BaseModel
import uuid
from datetime import datetime
from typing import Optional

class Amenity(BaseModel):
    """
    Représente une commodité (Amenity) dans le système.
    
    Attributs :
        - id : identifiant unique (UUID en string)
        - name : nom de la commodité
        - created_at : date de création (datetime)
        - updated_at : date de dernière modification (datetime)
    """

    def __init__(self, name: str):
        if not name:
            raise ValueError("Le nom de la commodité est obligatoire.")
        self.id = str(uuid.uuid4())  # UUID stocké directement en string
        self.name = name
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Met à jour la date de modification (simulateur de sauvegarde)."""
        self.updated_at = datetime.now()

    @classmethod
    def create(cls, name: str):
        """Crée et retourne une nouvelle commodité."""
        return cls(name)

    def update(self, name: Optional[str] = None):
        """Met à jour les attributs modifiables de la commodité."""
        if name:
            self.name = name
            self.save()

    def to_dict(self) -> dict:
        """
        Représente l'amenity sous forme de dictionnaire sérialisable en JSON.
        (utile pour Flask-RESTx / Swagger)
        """
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
