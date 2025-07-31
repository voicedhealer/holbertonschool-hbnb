from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app import db


class HBnBFacade:
    def __init__(self):
        self.user_repo = SQLAlchemyRepository(User)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.place_repo = SQLAlchemyRepository(Place)
        self.review_repo = SQLAlchemyRepository(Review)

    # ---------- USER ----------
    def create_user(self, user_data):
        """Création d'utilisateur avec gestion robuste des données"""
        # ✅ Debug pour voir les données reçues
        print(f"=== DEBUG FACADE CREATE_USER ===")
        print(f"Données reçues: {user_data}")
        print(f"Username: {user_data.get('username')}")
        print(f"Role: {user_data.get('role')}")
        print("===============================")
        
        try:
            # ✅ Validation des champs requis
            required_fields = ['first_name', 'last_name', 'email', 'username', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    raise ValueError(f"Field '{field}' is required")
            
            # ✅ Extraction du mot de passe pour traitement séparé
            password = user_data.pop('password')
            
            # ✅ Assurer que le rôle a une valeur par défaut
            if not user_data.get('role'):
                user_data['role'] = 'voyageur'
            
            # ✅ Création avec la méthode from_dict pour compatibilité
            user = User.from_dict(user_data)
            
            # ✅ Hash du mot de passe après création
            user.hash_password(password)
            
            # ✅ Sauvegarde en base avec commit
            self.user_repo.add(user)
            db.session.commit()
            
            # ✅ Debug de vérification
            print(f"Utilisateur créé avec succès: {user.to_dict()}")
            
            return user
            
        except Exception as e:
            print(f"❌ Erreur création utilisateur: {str(e)}")
            db.session.rollback()
            raise e

    def get_users(self):
        """Récupération de tous les utilisateurs"""
        return self.user_repo.get_all()

    def get_user(self, user_id):
        """Récupération d'un utilisateur par ID"""
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        """Récupération d'un utilisateur par email"""
        return self.user_repo.get_by_attribute('email', email)

    def get_user_by_username(self, username):
        """Récupération d'un utilisateur par username"""
        return self.user_repo.get_by_attribute('username', username)

    def update_user(self, user_id, user_data):
        """Mise à jour d'un utilisateur"""
        try:
            # ✅ Gestion spéciale pour le mot de passe
            if 'password' in user_data:
                user = self.get_user(user_id)
                if user:
                    password = user_data.pop('password')
                    user.hash_password(password)
            
            self.user_repo.update(user_id, user_data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # ---------- AMENITY ----------
    def create_amenity(self, amenity_data):
        """Création d'une amenité"""
        try:
            amenity = Amenity(**amenity_data)
            self.amenity_repo.add(amenity)
            db.session.commit()
            return amenity
        except Exception as e:
            db.session.rollback()
            raise e

    def get_amenity(self, amenity_id):
        """Récupération d'une amenité par ID"""
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        """Récupération de toutes les amenités"""
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Mise à jour d'une amenité"""
        try:
            self.amenity_repo.update(amenity_id, amenity_data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_amenity(self, amenity_id):
        """Suppression d'une amenité"""
        try:
            amenity = self.get_amenity(amenity_id)
            if not amenity:
                raise ValueError("Amenity not found")
            self.amenity_repo.delete(amenity_id)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # ---------- PLACE ----------
    def create_place(self, place_data):
        """Création d'un lieu avec validation complète"""
        try:
            # ✅ Debug
            print(f"=== DEBUG CREATE_PLACE ===")
            print(f"Données place: {place_data}")
            
            # 1. Vérification owner avec gestion d'erreur améliorée
            owner_id = place_data.get('owner_id')
            if not owner_id:
                raise ValueError('owner_id is required')
                
            owner = self.user_repo.get(owner_id)
            if not owner:
                raise ValueError(f'Invalid owner_id: {owner_id}')
            
            # ✅ Vérification que l'owner est bien propriétaire
            if owner.role != 'owner':
                raise ValueError('User must have owner role to create places')
            
            # 2. Amenities: charger les objets
            amenities = []
            amenities_ids = place_data.pop('amenities', [])
            for am_id in amenities_ids:
                amenity = self.get_amenity(am_id)
                if not amenity:
                    raise ValueError(f'Invalid amenity id: {am_id}')
                amenities.append(amenity)

            # 3. Création de la Place
            place_data['owner'] = owner
            place = Place(**place_data)
            self.place_repo.add(place)
            
            # 4. Ajout amenities à la place
            for amenity in amenities:
                if hasattr(place, 'add_amenity'):
                    place.add_amenity(amenity)
            
            # 5. Ajout place à l'owner
            if hasattr(owner, "add_place"):
                owner.add_place(place)
            
            db.session.commit()
            print(f"Place créée avec succès: {place.to_dict() if hasattr(place, 'to_dict') else place}")
            return place
            
        except Exception as e:
            print(f"❌ Erreur création place: {str(e)}")
            db.session.rollback()
            raise e

    def get_place(self, place_id):
        """Récupération d'un lieu par ID"""
        return self.place_repo.get(place_id)

    def get_all_places(self):
        """Récupération de tous les lieux"""
        return self.place_repo.get_all()

    def get_places_by_owner(self, owner_id):
        """Récupération des lieux par propriétaire"""
        return self.place_repo.get_by_attribute('owner_id', owner_id)

    def update_place(self, place_id, place_data):
        """Mise à jour d'un lieu"""
        try:
            # ✅ Vérification que le lieu existe
            place = self.get_place(place_id)
            if not place:
                raise ValueError("Place not found")
            
            # ✅ Gestion des amenities si présentes
            if 'amenities' in place_data:
                amenities_ids = place_data.pop('amenities', [])
                # Logique de mise à jour des amenities...
            
            self.place_repo.update(place_id, place_data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_place(self, place_id):
        """Suppression d'un lieu"""
        try:
            place = self.get_place(place_id)
            if not place:
                raise ValueError("Place not found")
            
            # Détacher des relations si nécessaire
            owner = getattr(place, 'owner', None)
            if owner and hasattr(owner, "remove_place"):
                owner.remove_place(place)
            
            self.place_repo.delete(place_id)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # ---------- REVIEW ----------
    def create_review(self, review_data):
        """Création d'un avis"""
        try:
            # ✅ Validation des utilisateurs et lieux
            user_id = review_data.get('user_id')
            place_id = review_data.get('place_id')
            
            if not user_id or not place_id:
                raise ValueError('user_id and place_id are required')
            
            user = self.user_repo.get(user_id)
            if not user:
                raise ValueError(f'Invalid user_id: {user_id}')
                
            place = self.place_repo.get(place_id)
            if not place:
                raise ValueError(f'Invalid place_id: {place_id}')
            
            # ✅ Vérification qu'un utilisateur ne review pas son propre lieu
            if hasattr(place, 'owner') and place.owner.id == user_id:
                raise ValueError('Owner cannot review their own place')
            
            review_data['user'] = user
            review_data['place'] = place
            review = Review(**review_data)
            self.review_repo.add(review)
            
            # Ajout aux relations
            if hasattr(user, "add_review"):
                user.add_review(review)
            if hasattr(place, "add_review"):
                place.add_review(review)
            
            db.session.commit()
            return review
            
        except Exception as e:
            db.session.rollback()
            raise e

    def get_review(self, review_id):
        """Récupération d'un avis par ID"""
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        """Récupération de tous les avis"""
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        """Récupération des avis par lieu"""
        place = self.place_repo.get(place_id)
        if not place:
            raise ValueError('Place not found')
        return getattr(place, "reviews", [])

    def get_reviews_by_user(self, user_id):
        """Récupération des avis par utilisateur"""
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError('User not found')
        return getattr(user, "reviews", [])

    def update_review(self, review_id, review_data):
        """Mise à jour d'un avis"""
        try:
            review = self.get_review(review_id)
            if not review:
                raise ValueError("Review not found")
            
            self.review_repo.update(review_id, review_data)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_review(self, review_id):
        """Suppression d'un avis"""
        try:
            review = self.review_repo.get(review_id)
            if not review:
                raise ValueError('Review not found')
            
            # Détacher des relations
            user = getattr(review, 'user', None)
            place = getattr(review, 'place', None)
            
            if user and hasattr(user, "remove_review"):
                user.remove_review(review)
            if place and hasattr(place, "remove_review"):
                place.remove_review(review)
            
            self.review_repo.delete(review_id)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # ---------- MÉTHODES UTILITAIRES ----------
    def get_user_by_credentials(self, identifier):
        """Récupération d'un utilisateur par email ou username"""
        # Essayer par email d'abord
        user = self.get_user_by_email(identifier)
        if not user:
            # Essayer par username
            user = self.get_user_by_username(identifier)
        return user

    def validate_owner_permissions(self, user_id, place_id):
        """Validation que l'utilisateur est propriétaire du lieu"""
        place = self.get_place(place_id)
        if not place:
            raise ValueError("Place not found")
        
        if not hasattr(place, 'owner') or place.owner.id != user_id:
            raise ValueError("User is not the owner of this place")
        
        return True

    def get_place_statistics(self, place_id):
        """Statistiques d'un lieu"""
        place = self.get_place(place_id)
        if not place:
            raise ValueError("Place not found")
        
        reviews = self.get_reviews_by_place(place_id)
        return {
            'total_reviews': len(reviews),
            'average_rating': sum(r.rating for r in reviews) / len(reviews) if reviews else 0,
            'place_id': place_id
        }
