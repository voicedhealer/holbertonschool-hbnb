from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()
with app.app_context():
    db.create_all()

    # Vérifie si un admin existe déjà
    admin = User.query.filter_by(email="admin@example.com").first()
    if not admin:
        admin = User(
            first_name="Admin",
            last_name="User",
            email="admin@example.com"
        )
        admin.set_password("adminpassword")
        admin.is_admin = True
        db.session.add(admin)
        db.session.commit()
        print("Admin créé avec succès !")
    else:
        print("Un admin existe déjà.")
