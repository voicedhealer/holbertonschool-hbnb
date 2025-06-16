from review import Review # importe la classe Review du fichier review
import uuid # importe module qui genere les uuid

# genere un uuid aleatoire pour l'utilisateur
user_id = uuid.uuid4()

# genere un uuid aleatoire pour l'endroit
place_id = uuid.uuid4()

# exemple de review
review = Review(user_id, place_id, "Super endroit calme et propre", 5)

# affiche toute les interactions de l'utilisateur
print("ID:", review.id)
print("User ID:", review.user_id)
print("Place ID:", review.place_id)
print("Text:", review.text)
print("Rating:", review.rating)
print("Comment:", review.comment)
print("Date submitted:", review.date_submission)
print("Created at:", review.created_at)
print("Updated at:", review.updated_at)
