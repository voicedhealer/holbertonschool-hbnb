from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # Créer un utilisateur
    def create_user(self, user_data):
        # user_data est un dictionnaire avec les infos de l'utilisateur
        user = self.user_repo.create(user_data)
        # On retire le mot de passe avant de retourner l'utilisateur
        if 'password' in user:
            user = dict(user)  # Copie pour ne pas modifier l'original
            user.pop('password')
        return user

    # Récupérer la liste de tous les utilisateurs
    def get_all_users(self):
        users = self.user_repo.get_all()
        # On retire le mot de passe pour chaque utilisateur
        return [
            {k: v for k, v in user.items() if k != 'password'}
            for user in users
        ]

    # Récupérer un utilisateur par ID
    def get_user(self, user_id):
        user = self.user_repo.get(user_id)
        if user is None:
            return None
        # On retire le mot de passe
        return {k: v for k, v in user.items() if k != 'password'}

    # Mettre à jour un utilisateur
    def update_user(self, user_id, update_data):
        user = self.user_repo.update(user_id, update_data)
        if user is None:
            return None
        # On retire le mot de passe
        return {k: v for k, v in user.items() if k != 'password'}

    # Exemple pour Place (à compléter selon la logique métier)
    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    # Ajoute ici les autres méthodes pour Place, Review, Amenity selon le même modèle
