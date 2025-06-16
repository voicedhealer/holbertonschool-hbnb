from base import BaseModel

class Review(BaseModel):

    
    def __init__(self, user_id, place_id, text, rating, comment=""):
    """Initialise une review avec l'ID du user, id de l'endroit, le texte et commentaire facultatif"""

        super().__init__()
        """Appelle le parent dans le constructeur"""

        self.user_id = user_id
        """UUID de l'utilisateur qui a écrit son avis"""

        self.place_id = place_id
        """UUID de l'endroit où l'avis a été écrit"""


        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        """Si l'avis n'est pas une chaine de caractère, il renvoie un message d'erreur """

        self.text = text
        """Contenu du review"""

        if not isinstance(rating, int):
            raise ValueError("Must be a number")
        """Si le rating n'est pas un nombre, il renvoie un message d'erreur"""

        if rating < 1 or rating > 5:
            raise ValueError("Number must be between 1 and 5")
        """Si le rating est inférieur à 1 ou supérieur à 5, il renvoie un message d'erreur """

        self.rating = rating
        """le rating"""

        if not isinstance(comment, str):
            raise ValueError("Comment must be a string")
        """SI le commentaire n'est pas une chaine de caractère, renvoie un message d'erreur"""

        self.comment = comment
        """le commentaire en lui même"""

        self.date_submission = datetime.now()
        """la date de la review"""
