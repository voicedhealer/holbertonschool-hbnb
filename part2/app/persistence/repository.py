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
    def update(self, obj
