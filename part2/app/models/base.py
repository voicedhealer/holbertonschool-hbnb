"""
Module définissant la classe de base pour tous les modèles de données.
"""
import uuid
from datetime import datetime
from typing import Any
from .base import BaseModel

class BaseModel:
    """
    Classe de base abstraite pour tous les modèles de données de l'application.

    Cette classe fournit un socle commun à toutes les entités métier (comme
    User, Place, etc.). Elle gère automatiquement :
    - L'assignation d'un identifiant unique (`id`).
    - Le suivi des timestamps de création (`created_at`) et de modification (`updated_at`).

    Elle offre également des méthodes utilitaires pour la mise à jour des objets.

    Attributes:
        id (str): Un identifiant unique universel (UUID) généré pour chaque instance.
        created_at (datetime): La date et l'heure exactes de la création de l'instance.
        updated_at (datetime): La date et l'heure de la dernière modification de l'instance.
                               Initialisé à la date de création.
    """

    def __init__(self):
        """
        Initialise une nouvelle instance de BaseModel.

        Lors de l'instanciation, un `id` unique est généré et les timestamps
        `created_at` et `updated_at` sont définis à l'heure actuelle.
        """
        self.id: str = str(uuid.uuid4())
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()

    def save(self) -> None:
        """
        Met à jour le timestamp de la dernière modification (`updated_at`).

        Cette méthode doit être appelée chaque fois que l'état de l'objet est
        modifié et que cette modification doit être considérée comme une "sauvegarde".
        """
        self.updated_at = datetime.now()

    def update(self, **kwargs: Any) -> None:
        """
        Met à jour les attributs de l'objet à partir de paires clé-valeur.

        Cette méthode parcourt les arguments-clés fournis et met à jour les
        attributs correspondants de l'instance s'ils existent déjà.
        Après la mise à jour des attributs, elle appelle automatiquement `save()`
        pour actualiser le timestamp `updated_at`.

        Args:
            **kwargs (Any): Paires clé-valeur où la clé est le nom d'un attribut
                            et la valeur est la nouvelle valeur à assigner.

        Example:
            >>> user = User(name="John", email="john@test.com")
            >>> user.update(name="Jonathan", non_existent_attr="ignore")
            >>> print(user.name)
            'Jonathan'
            # user.non_existent_attr n'a pas été créé.
        """
        for key, value in kwargs.items():
            # Met à jour l'attribut uniquement s'il existe déjà sur l'objet.
            # Cela évite de créer des attributs arbitraires.
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
