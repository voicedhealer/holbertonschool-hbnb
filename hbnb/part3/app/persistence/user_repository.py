from app.models.user import User
from app import db
from app.persistence.repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        """Recherche un utilisateur par email (retourne None si non trouvé)"""
        return self.model.query.filter_by(email=email).first()

    # Exemple d'extension possible :
    def get_user_by_username(self, username):
        """Recherche un utilisateur par username (retourne None si non trouvé)"""
        return self.model.query.filter_by(username=username).first()
