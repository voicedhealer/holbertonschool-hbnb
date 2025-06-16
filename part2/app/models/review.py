from base import BaseModel
from datetime import datetime

class Review(BaseModel):

    
    def __init__(self, user_id, place_id, text, rating, comment=""):
        """Initialise une review avec l'ID du user, id de l'endroit, le texte et commentaire facultatif"""
>>>>>>> 796812bb939c762af25140fa65d8ddc77b52da88

        super().__init__()
        """Appelle le parent dans le constructeur"""

        self.user_id = user_id
        """UUID de l'utilisateur qui a écrit son avis"""

        self.place_id = place_id
        """UUID de l'endroit où l'avis a été écrit"""

        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        """Si le texte n'est pas une chaine de caractère, il renvoie un message d'erreur """

        self.text = text
        """Contenu de la review"""

        if not isinstance(rating, int):
            raise ValueError("Must be a number")
        """Si le rating n'est pas un nombre, il renvoie un message d'erreur"""

        if rating < 1 or rating > 5:
            raise ValueError("Number must be between 1 and 5")
        """Si le rating est inférieur à 1 ou supérieur à 5, renvoie un message d'erreur """

        self.rating = rating
        """Le rating"""

        if not isinstance(comment, str):
            raise ValueError("Comment must be a string")
        """Si le commentaire n'est pas une chaine de caractère, renvoie un message d'erreur"""

        self.comment = comment
        """Le commentaire en lui même"""

        self.date_submission = datetime.now()
        """La date de la review"""
