from datetime import datetime
import uuid
from app.models.base import BaseModel

class Amenity(BaseModel):
    """
    Classe représentant une commodité (Amenity).

    Hérite de BaseModel pour avoir un id unique et des timestamps.
    """

    def __init__(self, name: str):
        super().__init__()
        if not name:
            raise ValueError("Le nom de la commodité est requis")
        self.name = name

    def update(self, name: str = None):
        """Met à jour le nom de l'amenity."""
        if name:
            self.name = name
            self.updated_at = datetime.now()

    def to_dict(self):
        """Retourne une représentation dict sérialisable de l'amenity."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
