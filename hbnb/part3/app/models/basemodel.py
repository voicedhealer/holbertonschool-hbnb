import uuid
from datetime import datetime

class BaseModel:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Mettre à jour l'horodatage updated_at chaque fois que l'objet est modifié"""
        self.updated_at = datetime.now()

    def update(self, data):
        """Mettre à jour les attributs de l'objet en fonction du dictionnaire fourni"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()  # Mettre à jour l'horodatage updated_at
        
    def is_max_length(self, name, value, max_length):
        if len(value) > max_length:
            raise ValueError(f"{name} must be {max_length} characters max.") 
    
    def is_between(self, name, value, min, max):
        if not min < value < max:
            raise ValueError(f"{name} must be between {min} and {max}.")
