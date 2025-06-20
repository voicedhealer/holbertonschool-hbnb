"""
Module définissant la Façade de services pour l'application HBnB.

Ce module contient la classe `HBnBFacade`, qui sert de point d'entrée unique
pour interagir avec la logique métier et la couche de persistance de données.
Elle simplifie l'interface pour les couches supérieures (comme l'API REST)
en orchestrant les opérations sur les différents dépôts de données.
"""
from typing import List, Dict, Optional, Any, Tuple, Union

from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity


class HBnBFacade:
    """
    Fournit une interface simplifiée pour la logique métier de l'application.

    Cette classe implémente le pattern Façade. Elle masque la complexité
    de l'interaction directe avec les dépôts de données (`Repository`) et
    centralise les règles métier (par exemple, la validation des données,
    la vérification des dépendances entre objets).

    Attributes:
        user_repo (InMemoryRepository): Dépôt pour la gestion des utilisateurs.
        place_repo (InMemoryRepository): Dépôt pour la gestion des lieux.
        review_repo (InMemoryRepository): Dépôt pour la gestion des avis.
        amenity_repo (InMemoryRepository): Dépôt pour la gestion des commodités.
    """

    def __init__(self):
        """Initialise la façade en créant une instance de dépôt pour chaque modèle."""
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # ==========================
    # Opérations sur les Users
    # ==========================

    def create_user(self, user_data):
        """
        Crée un nouvel utilisateur après validation.

        Effectue des vérifications métier avant la création :
        1.  Assure la présence des champs requis ('first_name', 'last_name', 'email').
        2.  Vérifie que l'adresse email n'est pas déjà utilisée.

        Args:
        user_data (Dict[str, Any]): Dictionnaire contenant les données du nouvel utilisateur.

        Returns:
        Tuple: (dictionnaire utilisateur ou message d'erreur, code HTTP)
        """
        # Validation des champs requis
        if not all(user_data.get(key) for key in ['first_name', 'last_name', 'email']):
            return {"message": "Missing required fields"}, 400

        # Vérification de l'unicité de l'email
        if self.get_user_by_email(user_data['email']):
            return {"message": "Email already exists"}, 400

        # Création de l'utilisateur
        user = User(**user_data)
        created_user = self.user_repo.create(user)
        user_dict = created_user.to_dict()  # Assure-toi que to_dict() retourne 'id'
        user_dict.pop('password', None)
        return user_dict, 201

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Récupère une liste de tous les utilisateurs."""
        users = self.user_repo.get_all()
        # Exclut le mot de passe de chaque utilisateur pour la sécurité
        return [{k: v for k, v in user.__dict__.items() if k != 'password'} for user in users]

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un utilisateur par son ID.

        Args:
            user_id (str): L'identifiant de l'utilisateur.

        Returns:
            Un dictionnaire représentant l'utilisateur (sans mot de passe),
            ou None si l'utilisateur n'est pas trouvé.
        """
        user = self.user_repo.get(user_id)
        if user is None:
            return None
        user_dict = user.__dict__
        user_dict.pop('password', None)
        return user_dict

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un objet utilisateur par son adresse email.

        Note : Cette méthode retourne l'objet User complet, y compris le mot de passe,
        car elle est destinée à un usage interne (ex: validation).

        Args:
            email (str): L'email de l'utilisateur à rechercher.

        Returns:
            L'objet User s'il est trouvé, sinon None.
        """
        return self.user_repo.get_by_attribute('email', email)

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Met à jour les informations d'un utilisateur.

        Args:
            user_id (str): L'ID de l'utilisateur à mettre à jour.
            update_data (Dict[str, Any]): Les données à modifier.

        Returns:
            Un dictionnaire de l'utilisateur mis à jour (sans mot de passe),
            ou None si l'utilisateur n'est pas trouvé.
        """
        user = self.user_repo.update(user_id, update_data)
        if user is None:
            return None
        user_dict = user.__dict__
        user_dict.pop('password', None)
        return user_dict

    def list_users(self):
        """Retourne la liste de tous les utilisateurs sous forme de dictionnaires."""
        users = self.user_repo.get_all()
        # Si vos utilisateurs sont des objets, convertissez-les en dicts si besoin
        return [user if isinstance(user, dict) else user.__dict__ for user in users]

    # ===========================
    # Opérations sur les Places
    # ===========================

    def create_place(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau lieu."""
        place = Place(**place_data)
        return self.place_repo.create(place).__dict__

    def get_all_places(self) -> List[Dict[str, Any]]:
        """Récupère une liste de tous les lieux."""
        return [p.__dict__ for p in self.place_repo.get_all()]

    def get_place(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un lieu par son ID."""
        place = self.place_repo.get(place_id)
        return place.__dict__ if place else None

    def update_place(self, place_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un lieu existant."""
        place = self.place_repo.update(place_id, update_data)
        return place.__dict__ if place else None

    # ============================
    # Opérations sur les Reviews
    # ============================

    def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crée une nouvelle review après validation des dépendances.

        Args:
            review_data (Dict[str, Any]): Données de la review.

        Returns:
            Un dictionnaire représentant la nouvelle review.

        Raises:
            ValueError: Si le texte de la review est manquant, ou si
                        l'utilisateur ou le lieu associé n'existe pas.
        """
        if not review_data.get('text'):
            raise ValueError("Review text is required")
        if not self.user_repo.get(review_data['user_id']):
            raise ValueError("User does not exist")
        if not self.place_repo.get(review_data['place_id']):
            raise ValueError("Place does not exist")
        
        review = Review(**review_data)
        return self.review_repo.create(review).__dict__

    def get_all_reviews(self) -> List[Dict[str, Any]]:
        """Récupère une liste de toutes les reviews."""
        return [r.__dict__ for r in self.review_repo.get_all()]

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une review par son ID."""
        review = self.review_repo.get(review_id)
        return review.__dict__ if review else None

    def update_review(self, review_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour une review existante."""
        review = self.review_repo.update(review_id, update_data)
        return review.__dict__ if review else None

    def delete_review(self, review_id: str) -> bool:
        """
        Supprime une review par son ID.

        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        return self.review_repo.delete(review_id)

    # =============================
    # Opérations sur les Amenities
    # =============================

    def create_amenity(self, amenity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle commodité (amenity)."""
        amenity = Amenity(**amenity_data)
        return self.amenity_repo.create(amenity).__dict__

    def get_all_amenities(self) -> List[Dict[str, Any]]:
        """Récupère une liste de toutes les commodités."""
        return [a.__dict__ for a in self.amenity_repo.get_all()]

    def get_amenity(self, amenity_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une commodité par son ID."""
        from uuid import UUID
        print(self.amenity_repo._storage.keys())
        uuid = UUID(amenity_id)
        amenity = self.amenity_repo.get(uuid)
        return amenity.__dict__ if amenity else None

    def update_amenity(self, amenity_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour une commodité existante."""
        amenity = self.amenity_repo.update(amenity_id, update_data)
        return amenity.__dict__ if amenity else None
