from app.models.base import BaseModel
from datetime import datetime
import uuid

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password=None, is_admin=False):
        """
        Constructeur de la classe User.
        Initialise un nouvel utilisateur avec prénom, nom, email et mot de passe.
        Appelle le constructeur de BaseModel pour initialiser id, created_at, updated_at.
        """
        super().__init__()
        self.id = str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password  # Mot de passe de l'utilisateur (à remplacer par un hash sécurisé en prod)
        self.is_admin = is_admin

    def update(self, **kwargs):
        """
        Met à jour les attributs de l'utilisateur avec les valeurs fournies dans kwargs.
        Met également à jour la date de modification (updated_at).
        Ne permet pas de modifier 'id', 'created_at', ou 'updated_at'.
        """
        protected_fields = {'id', 'created_at', 'updated_at'}
        for key, value in kwargs.items():
            if key not in protected_fields:
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def to_dict(self):
        """
        Retourne une représentation dictionnaire de l'utilisateur,
        sans le mot de passe ni les champs sensibles.
        """
        return {
        "id": self.id,
        "first_name": self.first_name,
        "last_name": self.last_name,
        "email": self.email
            # Ajoute ici d'autres champs publics si besoin, mais jamais le mot de passe !
        }