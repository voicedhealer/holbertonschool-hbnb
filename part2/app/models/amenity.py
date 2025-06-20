import uuid
from datetime import datetime
from app.models.base import BaseModel
from typing import Optional

class Amenity:
    """
    Classe représentant une commodité (Amenity) selon le diagramme de classes.
    Attributs :
        - id : UUID unique de l'amenity
        - name : nom de la commodité
        - created_at : date de création
        - updated_at : date de dernière modification
    Méthodes :
        - save() : enregistre/modifie la commodité
        - delete() : supprime la commodité
        - create() : ajoute une nouvelle commodité
        - update() : modifie la commodité
    """
    def __init__(self, name: str):
        if name is None:
            raise ValueError("Le nom de la commodité ne peut pas être None")
        self.id = uuid.uuid4()
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
        """Modifie la commodité (ex : changer le nom)."""
        if name:
            self.name = name
            self.save()

    def to_dict(self):
        """Représente l'amenity sous forme de dictionnaire (utile pour l'API ou la sérialisation)."""
        return {
            "id": str(self.id),
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
