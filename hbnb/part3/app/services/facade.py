from app.extensions import db
from app.models.user import User
from app.models.place import Place, PlaceAmenity
from app.models.amenity import Amenity
from app.models.review import Review
from werkzeug.security import generate_password_hash
import logging

# Configuration du logging pour debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HBnBFacade:

    # ---------- USER ----------
    def create_user(self, data):
        """Création d'utilisateur avec gestion complète des rôles"""
        logger.info(f"🔧 Création utilisateur: {data.get('email', 'Unknown')}")
        
        try:
            # ✅ Validation des données avec username et role
            required_fields = ['first_name', 'last_name', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    raise ValueError(f"Field '{field}' is required")
            
            # ✅ Vérification unicité email
            if User.query.filter_by(email=data['email']).first():
                raise ValueError("Email already registered")
            
            # ✅ Vérification unicité username si fourni
            if data.get('username') and User.query.filter_by(username=data['username']).first():
                raise ValueError("Username already registered")
            
            # ✅ Création avec tous les champs nécessaires
            user = User(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                username=data.get('username', ''),
                role=data.get('role', 'voyageur')  # ← IMPORTANT pour les propriétaires
            )
            
            user.set_password(data['password'])
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"✅ Utilisateur créé: {user.email} - Rôle: {user.role}")
            return user
            
        except Exception as e:
            logger.error(f"❌ Erreur création utilisateur: {str(e)}")
            db.session.rollback()
            raise e

    def get_user(self, user_id):
        """Récupération d'un utilisateur par ID"""
        try:
            return db.session.get(User, user_id)
        except Exception as e:
            logger.error(f"❌ Erreur récupération user {user_id}: {str(e)}")
            return None

    def get_user_by_email(self, email):
        """Récupération d'un utilisateur par email"""
        try:
            if not email:
                return None
            return User.query.filter_by(email=email.lower().strip()).first()
        except Exception as e:
            logger.error(f"❌ Erreur récupération user par email: {str(e)}")
            return None

    def get_user_by_username(self, username):
        """Récupération d'un utilisateur par username"""
        try:
            if not username:
                return None
            return User.query.filter_by(username=username.strip()).first()
        except Exception as e:
            logger.error(f"❌ Erreur récupération user par username: {str(e)}")
            return None

    def get_user_by_credentials(self, identifier):
        """Récupération d'un utilisateur par email ou username - CRUCIAL pour login"""
        try:
            if not identifier:
                return None
            
            # Essayer par email d'abord
            user = self.get_user_by_email(identifier)
            if not user:
                # Essayer par username
                user = self.get_user_by_username(identifier)
            
            return user
        except Exception as e:
            logger.error(f"❌ Erreur récupération credentials: {str(e)}")
            return None

    def get_all_users(self):
        """Récupération de tous les utilisateurs"""
        try:
            return User.query.all()
        except Exception as e:
            logger.error(f"❌ Erreur récupération users: {str(e)}")
            return []

    def update_user(self, user_id, data):
        """Mise à jour d'un utilisateur avec gestion du rôle"""
        try:
            user = self.get_user(user_id)
            if not user:
                return None
                
            # Vérification unicité email
            if 'email' in data and data['email'] != user.email:
                if self.get_user_by_email(data['email']):
                    raise ValueError("Email already registered")
                user.email = data['email']
            
            # Vérification unicité username
            if 'username' in data and data['username'] != user.username:
                if self.get_user_by_username(data['username']):
                    raise ValueError("Username already registered")
                user.username = data['username']
            
            # Mise à jour des autres champs
            updatable_fields = ['first_name', 'last_name', 'role']
            for field in updatable_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            if 'password' in data:
                user.set_password(data['password'])
                
            db.session.commit()
            logger.info(f"✅ Utilisateur {user_id} mis à jour")
            return user
            
        except Exception as e:
            logger.error(f"❌ Erreur update user: {str(e)}")
            db.session.rollback()
            raise e

    def delete_user(self, user_id):
        """Supprimer un utilisateur (avec ses lieux et avis)"""
        try:
            user = self.get_user(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Supprimer les lieux de l'utilisateur (et leurs relations)
            user_places = Place.query.filter_by(owner_id=user_id).all()
            for place in user_places:
                self.delete_place(place.id)
            
            # Supprimer les avis de l'utilisateur
            Review.query.filter_by(user_id=user_id).delete()
            
            # Supprimer l'utilisateur
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"✅ Utilisateur {user_id} supprimé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur delete user: {str(e)}")
            db.session.rollback()
            raise e

    # ---------- AMENITY ----------
    def create_amenity(self, data):
        """Création d'une amenité"""
        try:
            Amenity.validate_data(data)
            if Amenity.query.filter_by(name=data['name']).first():
                raise ValueError("Amenity name must be unique")
                
            amenity = Amenity(name=data['name'])
            db.session.add(amenity)
            db.session.commit()
            
            logger.info(f"✅ Amenity créée: {amenity.name}")
            return amenity
            
        except Exception as e:
            logger.error(f"❌ Erreur création amenity: {str(e)}")
            db.session.rollback()
            raise e

    def get_amenity(self, amenity_id):
        """Récupération d'une amenité par ID"""
        try:
            return db.session.get(Amenity, amenity_id)
        except Exception as e:
            logger.error(f"❌ Erreur récupération amenity: {str(e)}")
            return None

    def get_all_amenities(self):
        """Récupération de toutes les amenités"""
        try:
            return Amenity.query.all()
        except Exception as e:
            logger.error(f"❌ Erreur récupération amenities: {str(e)}")
            return []

    def update_amenity(self, amenity_id, data):
        """Mise à jour d'une amenité"""
        try:
            amenity = self.get_amenity(amenity_id)
            if not amenity:
                return None
                
            if 'name' in data:
                if not data['name'] or len(data['name']) > 50:
                    raise ValueError("Amenity name is required and must be <= 50 chars")
                    
                existing = Amenity.query.filter_by(name=data['name']).first()
                if existing and existing.id != amenity_id:
                    raise ValueError("Amenity name must be unique")
                    
                amenity.name = data['name']
                
            db.session.commit()
            return amenity
            
        except Exception as e:
            logger.error(f"❌ Erreur update amenity: {str(e)}")
            db.session.rollback()
            raise e

    def delete_amenity(self, amenity_id):
        """Supprimer un équipement (et ses relations avec les lieux)"""
        try:
            amenity = self.get_amenity(amenity_id)
            if not amenity:
                raise ValueError("Amenity not found")
            
            # Supprimer les relations avec les lieux
            PlaceAmenity.query.filter_by(amenity_id=amenity_id).delete()
            
            # Supprimer l'équipement
            db.session.delete(amenity)
            db.session.commit()
            
            logger.info(f"✅ Amenity {amenity_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur delete amenity: {str(e)}")
            db.session.rollback()
            raise e

    # ---------- PLACE ----------
    def create_place(self, data):
        """Création d'un lieu avec validation du rôle propriétaire"""
        logger.info(f"🔧 Création place: {data.get('title', 'Unknown')}")
        
        try:
            Place.validate_data(data)
            
            # ✅ Validation owner avec vérification du rôle
            owner_id = data.get('owner_id')
            if not owner_id:
                raise ValueError("owner_id is required")
                
            owner = db.session.get(User, owner_id)
            if not owner:
                raise ValueError(f"Owner not found: {owner_id}")
            
            # ✅ VÉRIFICATION CRUCIALE : L'utilisateur doit être propriétaire
            if not hasattr(owner, 'role') or owner.role != 'owner':
                raise ValueError(f"User must have 'owner' role to create places. Current role: {getattr(owner, 'role', 'undefined')}")
            
            # Validation et récupération des amenities
            amenities = []
            for amenity_id in data.get('amenities', []):
                if not amenity_id:
                    raise ValueError("Amenity ID cannot be empty")
                amenity = db.session.get(Amenity, amenity_id)
                if not amenity:
                    raise ValueError(f"Amenity not found: {amenity_id}")
                amenities.append(amenity)
            
            # Création du lieu
            place = Place(
                title=data['title'],
                description=data.get('description', ''),
                price=data['price'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                owner_id=owner.id
            )
            
            db.session.add(place)
            db.session.flush()  # Pour obtenir l'ID du place

            # Ajout des amenities
            for amenity in amenities:
                pa = PlaceAmenity(place_id=place.id, amenity_id=amenity.id)
                db.session.add(pa)
                
            db.session.commit()
            
            logger.info(f"✅ Place créée: {place.title} par {owner.email}")
            return place
            
        except Exception as e:
            logger.error(f"❌ Erreur création place: {str(e)}")
            db.session.rollback()
            raise e

    def get_place(self, place_id):
        """Récupération d'un lieu par ID"""
        try:
            return db.session.get(Place, place_id)
        except Exception as e:
            logger.error(f"❌ Erreur récupération place: {str(e)}")
            return None

    def get_all_places(self):
        """Récupération de tous les lieux"""
        try:
            return Place.query.all()
        except Exception as e:
            logger.error(f"❌ Erreur récupération places: {str(e)}")
            return []

    def get_places_by_owner(self, owner_id):
        """Récupération des lieux par propriétaire"""
        try:
            return Place.query.filter_by(owner_id=owner_id).all()
        except Exception as e:
            logger.error(f"❌ Erreur récupération places owner: {str(e)}")
            return []

    def update_place(self, place_id, data):
        """Mise à jour d'un lieu"""
        try:
            place = self.get_place(place_id)
            if not place:
                return None
                
            # Mise à jour des champs simples
            updatable = ['title', 'description', 'price', 'latitude', 'longitude']
            for key in updatable:
                if key in data:
                    setattr(place, key, data[key])
                    
            # Mise à jour du propriétaire si nécessaire
            if 'owner_id' in data:
                owner = db.session.get(User, data['owner_id'])
                if not owner:
                    raise ValueError("Owner not found")
                if owner.role != 'owner':
                    raise ValueError("User must have 'owner' role")
                place.owner_id = owner.id
                
            # Mise à jour des amenities
            if 'amenities' in data:
                PlaceAmenity.query.filter_by(place_id=place.id).delete()
                for amenity_id in data['amenities']:
                    if not amenity_id:
                        raise ValueError("Amenity ID cannot be empty")
                    amenity = db.session.get(Amenity, amenity_id)
                    if not amenity:
                        raise ValueError(f"Amenity not found: {amenity_id}")
                    pa = PlaceAmenity(place_id=place.id, amenity_id=amenity.id)
                    db.session.add(pa)
                    
            db.session.commit()
            logger.info(f"✅ Place {place_id} mise à jour")
            return place
            
        except Exception as e:
            logger.error(f"❌ Erreur update place: {str(e)}")
            db.session.rollback()
            raise e

    def delete_place(self, place_id):
        """Supprimer un lieu par son ID avec toutes ses relations"""
        try:
            place = self.get_place(place_id)
            if not place:
                raise ValueError("Place not found")
            
            # 1. Supprimer les relations avec les équipements
            PlaceAmenity.query.filter_by(place_id=place_id).delete()
            
            # 2. Supprimer les avis du lieu
            Review.query.filter_by(place_id=place_id).delete()
            
            # 3. Supprimer le lieu lui-même
            db.session.delete(place)
            
            # 4. Confirmer toutes les suppressions
            db.session.commit()
            
            logger.info(f"✅ Place {place_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur delete place: {str(e)}")
            db.session.rollback()
            raise e

    def find_place_by_location(self, latitude, longitude, delta=1e-7):
        """Recherche d'un lieu par coordonnées géographiques"""
        try:
            return Place.query.filter(
                db.func.abs(Place.latitude - latitude) < delta,
                db.func.abs(Place.longitude - longitude) < delta
            ).first()
        except Exception as e:
            logger.error(f"❌ Erreur recherche par location: {str(e)}")
            return None

    # ---------- REVIEW ----------
    def create_review(self, data):
        """Création d'un avis avec validations"""
        try:
            Review.validate_data(data)
            
            user = db.session.get(User, data['user_id'])
            place = db.session.get(Place, data['place_id'])
            
            if not user:
                raise ValueError("User not found")
            if not place:
                raise ValueError("Place not found")
            
            # ✅ Vérification qu'un propriétaire ne peut pas reviewer son propre lieu
            if hasattr(place, 'owner_id') and str(place.owner_id) == str(user.id):
                raise ValueError("Owner cannot review their own place")
            
            review = Review(
                text=data['text'],
                rating=int(data['rating']),
                user_id=user.id,
                place_id=place.id
            )
            
            db.session.add(review)
            db.session.commit()
            
            logger.info(f"✅ Review créée pour place {place.id}")
            return review
            
        except Exception as e:
            logger.error(f"❌ Erreur création review: {str(e)}")
            db.session.rollback()
            raise e

    def get_review(self, review_id):
        """Récupération d'un avis par ID"""
        try:
            return db.session.get(Review, review_id)
        except Exception as e:
            logger.error(f"❌ Erreur récupération review: {str(e)}")
            return None

    def get_all_reviews(self):
        """Récupération de tous les avis"""
        try:
            return Review.query.all()
        except Exception as e:
            logger.error(f"❌ Erreur récupération reviews: {str(e)}")
            return []

    def get_reviews_by_place(self, place_id):
        """Récupération des avis par lieu"""
        try:
            place = db.session.get(Place, place_id)
            if not place:
                return None
            return list(place.reviews)
        except Exception as e:
            logger.error(f"❌ Erreur récupération reviews place: {str(e)}")
            return []

    def get_reviews_by_user(self, user_id):
        """Récupération des avis par utilisateur"""
        try:
            return Review.query.filter_by(user_id=user_id).all()
        except Exception as e:
            logger.error(f"❌ Erreur récupération reviews user: {str(e)}")
            return []

    def update_review(self, review_id, data):
        """Mise à jour d'un avis"""
        try:
            review = self.get_review(review_id)
            if not review:
                return None
                
            if 'text' in data:
                review.text = data['text']
                
            if 'rating' in data:
                rating = data['rating']
                if not (1 <= int(rating) <= 5):
                    raise ValueError("Rating must be between 1 and 5")
                review.rating = int(rating)
                
            db.session.commit()
            return review
            
        except Exception as e:
            logger.error(f"❌ Erreur update review: {str(e)}")
            db.session.rollback()
            raise e

    def delete_review(self, review_id):
        """Supprimer un avis par son ID"""
        try:
            review = self.get_review(review_id)
            if not review:
                raise ValueError("Review not found")
            
            db.session.delete(review)
            db.session.commit()
            
            logger.info(f"✅ Review {review_id} supprimée")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur delete review: {str(e)}")
            db.session.rollback()
            raise e

    # ---------- MÉTHODES UTILITAIRES ----------
    def validate_owner_permissions(self, user_id, place_id):
        """Validation des permissions propriétaire"""
        try:
            place = self.get_place(place_id)
            if not place:
                raise ValueError("Place not found")
            
            if not hasattr(place, 'owner_id') or str(place.owner_id) != str(user_id):
                raise ValueError("User is not the owner of this place")
            
            return True
        except Exception as e:
            logger.error(f"❌ Erreur validation permissions: {str(e)}")
            raise e

    def get_user_statistics(self, user_id):
        """Statistiques d'un utilisateur"""
        try:
            user = self.get_user(user_id)
            if not user:
                return None
            
            reviews = self.get_reviews_by_user(user_id)
            places = self.get_places_by_owner(user_id) if getattr(user, 'role', '') == 'owner' else []
            
            return {
                'user_id': user_id,
                'total_reviews': len(reviews),
                'total_places': len(places),
                'user_role': getattr(user, 'role', 'undefined')
            }
        except Exception as e:
            logger.error(f"❌ Erreur statistiques user: {str(e)}")
            return None
