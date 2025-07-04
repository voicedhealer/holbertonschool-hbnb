from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

# Crée une instance de l'application Flask
app = create_app()

# Crée les tables dans le contexte de l'application
with app.app_context():
    db.create_all()
    print("Base de données initialisée avec succès.")
