"""
Module définissant le design pattern Repository pour l'accès aux données.

Ce module contient une classe de base abstraite (Repository) qui définit une
interface commune pour les opérations de persistance des données (CRUD), et une
implémentation concrète (InMemoryRepository) qui stocke les données en mémoire,
idéale pour les tests ou les applications simples.
"""

from abc import ABC, abstractmethod
import uuid
from typing import List, Any, Optional

class Repository(ABC):
    """
    Définit une interface abstraite pour un dépôt de données (Repository).

    Le pattern Repository a pour but de découpler la logique métier de la couche
    d'accès aux données. Toute classe qui hérite de `Repository` doit implémenter
    les méthodes CRUD standard, garantissant ainsi une manière cohérente
    d'interagir avec la source de données (base de données, API, fichier, etc.).
    """

    @abstractmethod
    def add(self, obj: Any) -> None:
        """
        Ajoute un nouvel objet au dépôt.

        Args:
            obj (Any): L'objet à ajouter, supposé avoir un attribut 'id'.
        """
        pass

    @abstractmethod
    def get(self, obj_id: str) -> Optional[Any]:
        """
        Récupère un objet par son identifiant unique.

        Args:
            obj_id (str): L'identifiant de l'objet à récupérer.

        Returns:
            Optional[Any]: L'objet trouvé, ou None si aucun objet ne correspond.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Any]:
        """
        Récupère tous les objets du dépôt.

        Returns:
            List[Any]: Une liste de tous les objets. La liste peut être vide.
        """
        pass

    @abstractmethod
    def update(self, obj_id: str, data: dict) -> Optional[Any]:
        """
        Met à jour un objet existant identifié par son ID.

        Args:
            obj_id (str): L'identifiant de l'objet à mettre à jour.
            data (dict): Un dictionnaire contenant les données à mettre à jour.

        Returns:
            Optional[Any]: L'objet mis à jour, ou None si l'objet n'a pas été trouvé.
        """
        pass

    @abstractmethod
    def delete(self, obj_id: str) -> bool:
        """
        Supprime un objet du dépôt par son identifiant.

        Args:
            obj_id (str): L'identifiant de l'objet à supprimer.
        
        Returns:
            bool: True si la suppression a réussi, False sinon.
        """
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name: str, attr_value: Any) -> Optional[Any]:
        """
        Récupère le premier objet correspondant à un attribut et sa valeur.

        Args:
            attr_name (str): Le nom de l'attribut sur lequel rechercher.
            attr_value (Any): La valeur que l'attribut doit avoir.

        Returns:
            Optional[Any]: Le premier objet trouvé correspondant au critère,
                           ou None si aucun objet ne correspond.
        """
        pass


class InMemoryRepository(Repository):
    """
    Implémentation concrète d'un dépôt qui stocke les données en mémoire.

    Cette classe utilise un dictionnaire Python comme système de stockage. Elle est
    particulièrement utile pour le prototypage rapide, les tests unitaires et les
    applications ne nécessitant pas de persistance des données entre les sessions.

    Attributes:
        _storage (dict): Dictionnaire servant de base de données en mémoire.
                         Les clés sont les ID des objets, les valeurs sont les objets eux-mêmes.
    """
    def __init__(self):
        """Initialise un nouveau dépôt en mémoire avec un stockage vide."""
        self._storage = {}

    def add(self, obj: Any) -> None:
        """
        Ajoute un objet au dictionnaire de stockage en utilisant son ID comme clé.

        Cette méthode suppose que l'objet fourni possède déjà un attribut `id`.
        Pour une création avec génération d'ID, utilisez la méthode `create`.

        Args:
            obj (Any): L'objet à stocker.
        """
        self._storage[obj.id] = obj

    def get(self, obj_id: str) -> Optional[Any]:
        """
        Récupère un objet du stockage en mémoire par son ID.

        Args:
            obj_id (str): L'identifiant de l'objet à trouver.

        Returns:
            Optional[Any]: L'objet si trouvé, sinon None.
        """
        return self._storage.get(obj_id)

    def get_all(self) -> List[Any]:
        """Retourne une liste de tous les objets présents dans le dépôt."""
        return list(self._storage.values())

    def create(self, obj: Any) -> Any:
        """
        Crée et ajoute un objet, en lui assignant un UUID si nécessaire.

        Si l'objet fourni n'a pas d'attribut `id`, un UUIDv4 unique lui est
        assigné avant de l'ajouter au stockage.

        Args:
            obj (Any): L'objet à créer et à stocker.

        Returns:
            Any: L'objet avec son ID assigné.
        """
        if not hasattr(obj, 'id') or not obj.id:
            obj.id = str(uuid.uuid4())
        self.add(obj)
        return obj

    def update(self, obj_id: str, data: dict) -> Optional[Any]:
        """
        Met à jour un objet existant avec de nouvelles données.

        Recherche l'objet par son ID, puis appelle la méthode `update` de l'objet
        lui-même (il est supposé en avoir une) avec les nouvelles données.

        Args:
            obj_id (str): L'ID de l'objet à mettre à jour.
            data (dict): Les données à appliquer.

        Returns:
            Optional[Any]: L'objet mis à jour, ou None s'il n'a pas été trouvé.
        """
        obj = self.get(obj_id)
        if obj and hasattr(obj, 'update'):
            obj.update(**data)  # Suppose que l'objet a une méthode update
            self._storage[obj_id] = obj # S'assurer que la référence est à jour
            return obj
        return None

    def delete(self, obj_id: str) -> bool:
        """
        Supprime un objet du stockage en mémoire.

        Args:
            obj_id (str): L'ID de l'objet à supprimer.

        Returns:
            bool: True si l'objet existait et a été supprimé, False sinon.
        """
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name: str, attr_value: Any) -> Optional[Any]:
        """
        Recherche le premier objet correspondant à une paire attribut/valeur.

        Utilise une expression génératrice pour parcourir les objets de manière
        efficace et s'arrête dès qu'une correspondance est trouvée.

        Args:
            attr_name (str): Le nom de l'attribut à vérifier.
            attr_value (Any): La valeur attendue pour cet attribut.

        Returns:
            Optional[Any]: L'objet trouvé, ou None si aucun ne correspond.
        """
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name, None) == attr_value), None)

    def clear(self) -> None:
        """
        Vide complètement le dépôt.

        Principalement utile pour les tests afin de réinitialiser l'état
        entre chaque cas de test.
        """
        self._storage = {}
