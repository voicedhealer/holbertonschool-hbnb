from base import BaseModel
from datetime import datetime


class User(BaseModel):
    def __init__(self, first_name, last_name, email, password):
        """
        Constructeur de la classe User.
        Initialise un nouvel utilisateur avec prénom, nom, email et mot de passe.
        Appelle le constructeur de BaseModel pour initialiser id, created_at, updated_at.
        """
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password  # Mot de passe de l'utilisateur (à remplacer par un hash sécurisé en prod)

    def update(self, **kwargs):
        """
        Met à jour les attributs de l'utilisateur avec les valeurs fournies dans kwargs.
        Met également à jour la date de modification (updated_at).
        """
        for key, value in kwargs.items():
            setattr(self, key, value)  # Met à jour chaque attribut passé en argument
        self.updated_at = datetime.now()  # Met à jour la date de dernière modification
