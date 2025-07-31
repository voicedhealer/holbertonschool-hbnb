from .basemodel import BaseModel
from app import db, bcrypt
from flask_login import UserMixin
import re
import uuid
from datetime import datetime


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # ---------- Colonnes SQLAlchemy ----------
    id = db.Column(db.String(60), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    username = db.Column(db.String(80)) 
    profile_picture = db.Column(db.String(255))
    role = db.Column(db.String(20), default='voyageur')

    # ---------- Constructeur SÉCURISÉ ----------
    def __init__(self, first_name=None, last_name=None, email=None, username=None, 
                 password=None, role="voyageur", is_admin=False, profile_picture=None, **kwargs):
        super().__init__()
        
        print(f"🔧 User.__init__ appelé avec:")
        print(f"   first_name: {first_name or kwargs.get('first_name')}")
        print(f"   last_name: {last_name or kwargs.get('last_name')}")
        print(f"   email: {email or kwargs.get('email')}")
        print(f"   username: {username or kwargs.get('username')}")
        print(f"   role: {role or kwargs.get('role')}")
        
        # ✅ Gestion SÉCURISÉE des valeurs None avec double protection
        self.first_name = (kwargs.get('first_name') or first_name) or ''
        self.last_name = (kwargs.get('last_name') or last_name) or ''
        self.email = (kwargs.get('email') or email) or ''
        self.username = (kwargs.get('username') or username) or ''
        self.role = (kwargs.get('role') or role) or 'voyageur'
        self.is_admin = kwargs.get('is_admin', is_admin) or False
        self.profile_picture = kwargs.get('profile_picture', profile_picture)
        
        # ✅ Auto-assignation de l'ID si pas fourni
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid.uuid4())
        
        # ✅ Validation des champs requis APRÈS assignation sécurisée
        self._validate_required_fields()
        
        # ✅ Validation et nettoyage seulement si les champs ne sont pas vides
        if self.first_name and self.last_name and self.email and self.username:
            self._validate_and_clean()
        
        # ✅ Hash du mot de passe
        password_to_hash = kwargs.get('password', password)
        if password_to_hash:
            self.hash_password(password_to_hash)
        
        # Relations virtuelles
        self.places = []
        self.reviews = []
        
        print(f"🔧 User créé: username='{self.username}', role='{self.role}'")

    def _validate_required_fields(self):
        """Validation que les champs requis ne sont pas vides"""
        if not self.first_name or not str(self.first_name).strip():
            raise ValueError("First name is required")
        if not self.last_name or not str(self.last_name).strip():
            raise ValueError("Last name is required")
        if not self.email or not str(self.email).strip():
            raise ValueError("Email is required")
        if not self.username or not str(self.username).strip():
            raise ValueError("Username is required")

    def _validate_and_clean(self):
        """Validation et nettoyage des données SÉCURISÉ"""
        try:
            # ✅ Email - Validation sécurisée
            if self.email:
                self.email = str(self.email).strip().lower()
                if not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
                    raise ValueError("Invalid email format")
            
            # ✅ Noms - Nettoyage sécurisé
            if self.first_name:
                self.first_name = str(self.first_name).strip()
                if len(self.first_name) == 0:
                    raise ValueError("First name cannot be empty")
                if len(self.first_name) > 50:
                    raise ValueError("First name too long (50 max)")
            
            if self.last_name:
                self.last_name = str(self.last_name).strip()
                if len(self.last_name) == 0:
                    raise ValueError("Last name cannot be empty")
                if len(self.last_name) > 50:
                    raise ValueError("Last name too long (50 max)")
            
            # ✅ Username - Nettoyage sécurisé
            if self.username:
                self.username = str(self.username).strip()
                if len(self.username) == 0:
                    raise ValueError("Username cannot be empty")
                if len(self.username) > 80:
                    raise ValueError("Username too long (80 max)")
            
            # ✅ Role - Validation
            if self.role and self.role not in ('owner', 'voyageur'):
                print(f"⚠️ Rôle invalide '{self.role}', utilisation de 'voyageur'")
                self.role = 'voyageur'
                
        except AttributeError as e:
            print(f"❌ AttributeError dans _validate_and_clean: {str(e)}")
            # En cas d'erreur, assigner des valeurs par défaut
            if not hasattr(self, 'first_name') or self.first_name is None:
                self.first_name = ''
            if not hasattr(self, 'last_name') or self.last_name is None:
                self.last_name = ''
            if not hasattr(self, 'email') or self.email is None:
                self.email = ''
            if not hasattr(self, 'username') or self.username is None:
                self.username = ''
            raise e
        except Exception as e:
            print(f"❌ Erreur dans _validate_and_clean: {str(e)}")
            raise e

    # ---------- Mot de passe (utilise password_hash) ----------
    def hash_password(self, password_to_hash):
        if not password_to_hash:
            raise ValueError("Password cannot be empty")
        if len(str(password_to_hash)) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = bcrypt.generate_password_hash(str(password_to_hash)).decode('utf-8')

    def check_password(self, password_to_check):
        if not password_to_check or not self.password_hash:
            return False
        return bcrypt.check_password_hash(self.password_hash, str(password_to_check))

    # ---------- Méthodes de validation ----------
    def validate_email_unique(self, email):
        """Vérifier que l'email n'existe pas déjà"""
        if not email:
            return False
        existing_user = User.query.filter_by(email=email).first()
        return existing_user is None or existing_user.id == self.id

    def validate_username_unique(self, username):
        """Vérifier que le username n'existe pas déjà"""
        if not username:
            return False
        existing_user = User.query.filter_by(username=username).first()
        return existing_user is None or existing_user.id == self.id

    # ---------- Relations "mémoire" ----------
    def add_place(self, place):
        if not hasattr(self, 'places'):
            self.places = []
        self.places.append(place)
        
    def add_review(self, review):
        if not hasattr(self, 'reviews'):
            self.reviews = []
        self.reviews.append(review)
        
    def delete_review(self, review):
        if hasattr(self, 'reviews') and review in self.reviews:
            self.reviews.remove(review)

    # ---------- Export API / Front ----------
    def to_dict(self):
        result = {
            'id': str(self.id) if self.id else None,
            'first_name': str(self.first_name) if self.first_name else '',
            'last_name': str(self.last_name) if self.last_name else '',
            'email': str(self.email) if self.email else '',
            'username': str(self.username) if self.username else '',
            'role': str(self.role) if self.role else 'voyageur',
            'profile_picture': self.profile_picture,
            'is_admin': bool(self.is_admin) if self.is_admin is not None else False
        }
        
        print(f"🔧 to_dict() retourne: username='{result['username']}', role='{result['role']}'")
        return result

    # ✅ Méthode de création depuis données API
    @classmethod
    def from_dict(cls, data):
        """Créer un utilisateur depuis un dictionnaire (API)"""
        print(f"🔧 User.from_dict() appelé avec: {data}")
        
        if not data:
            raise ValueError("Data cannot be None or empty")
        
        # ✅ Validation des données requises avec protection None
        required_fields = ['first_name', 'last_name', 'email', 'username']
        for field in required_fields:
            if not data.get(field) or str(data.get(field)).strip() == '':
                raise ValueError(f"Field '{field}' is required and cannot be empty")
        
        try:
            instance = cls(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email'),
                username=data.get('username'),
                password=data.get('password'),
                role=data.get('role', 'voyageur'),
                is_admin=data.get('is_admin', False),
                profile_picture=data.get('profile_picture')
            )
            
            print(f"🔧 User.from_dict() créé: username={instance.username}, role={instance.role}")
            return instance
            
        except Exception as e:
            print(f"❌ Erreur dans User.from_dict(): {str(e)}")
            raise e

    # ---------- Méthodes utilitaires ----------
    def update_from_dict(self, data):
        """Mettre à jour un utilisateur depuis un dictionnaire"""
        if not data:
            return
            
        updatable_fields = ['first_name', 'last_name', 'email', 'username', 'role', 'is_admin', 'profile_picture']
        
        for field in updatable_fields:
            if field in data and data[field] is not None:
                setattr(self, field, data[field])
        
        # Revalidation après mise à jour
        try:
            self._validate_and_clean()
        except Exception as e:
            print(f"⚠️ Erreur lors de la revalidation: {str(e)}")
        
        # Mise à jour du mot de passe si fourni
        if 'password' in data and data['password']:
            self.hash_password(data['password'])

    def is_owner(self):
        """Vérifier si l'utilisateur est propriétaire"""
        return str(self.role).lower() == 'owner' if self.role else False

    def can_create_places(self):
        """Vérifier si l'utilisateur peut créer des lieux"""
        return self.is_owner()

    def can_review_place(self, place):
        """Vérifier si l'utilisateur peut reviewer un lieu"""
        if not place:
            return False
        # Un propriétaire ne peut pas reviewer son propre lieu
        if hasattr(place, 'owner') and place.owner and str(place.owner.id) == str(self.id):
            return False
        return True

    def get_full_name(self):
        """Obtenir le nom complet"""
        first = str(self.first_name) if self.first_name else ''
        last = str(self.last_name) if self.last_name else ''
        return f"{first} {last}".strip()

    # ---------- Méthodes de requête ----------
    @classmethod
    def find_by_email(cls, email):
        """Trouver un utilisateur par email"""
        if not email:
            return None
        try:
            return cls.query.filter_by(email=str(email).lower().strip()).first()
        except Exception as e:
            print(f"❌ Erreur find_by_email: {str(e)}")
            return None

    @classmethod
    def find_by_username(cls, username):
        """Trouver un utilisateur par username"""
        if not username:
            return None
        try:
            return cls.query.filter_by(username=str(username).strip()).first()
        except Exception as e:
            print(f"❌ Erreur find_by_username: {str(e)}")
            return None

    @classmethod
    def find_by_credentials(cls, identifier):
        """Trouver un utilisateur par email ou username"""
        if not identifier:
            return None
        user = cls.find_by_email(identifier)
        if not user:
            user = cls.find_by_username(identifier)
        return user

    @classmethod
    def get_owners(cls):
        """Récupérer tous les propriétaires"""
        try:
            return cls.query.filter_by(role='owner').all()
        except Exception as e:
            print(f"❌ Erreur get_owners: {str(e)}")
            return []

    @classmethod
    def get_travelers(cls):
        """Récupérer tous les voyageurs"""
        try:
            return cls.query.filter_by(role='voyageur').all()
        except Exception as e:
            print(f"❌ Erreur get_travelers: {str(e)}")
            return []

    # ---------- Validation avant sauvegarde ----------
    def __setattr__(self, name, value):
        """Validation automatique lors de l'assignation SÉCURISÉE"""
        if name in ['email', 'username', 'first_name', 'last_name', 'role'] and hasattr(self, name):
            try:
                # Validation spécifique selon le champ
                if name == 'email' and value:
                    value_str = str(value).strip().lower()
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", value_str):
                        raise ValueError("Invalid email format")
                    value = value_str
                elif name == 'role' and value:
                    if str(value) not in ('owner', 'voyageur'):
                        print(f"⚠️ Rôle invalide '{value}', utilisation de 'voyageur'")
                        value = 'voyageur'
                elif name in ['first_name', 'last_name', 'username'] and value:
                    value = str(value).strip()
                    if len(value) == 0:
                        raise ValueError(f"{name} cannot be empty")
            except Exception as e:
                print(f"⚠️ Erreur validation {name}: {str(e)}")
                # En cas d'erreur, on garde la valeur mais on la nettoie
                if value is not None:
                    value = str(value)
        
        super().__setattr__(name, value)

    def __repr__(self):
        username = str(self.username) if self.username else 'No username'
        role = str(self.role) if self.role else 'No role'
        email = str(self.email) if self.email else 'No email'
        return f'<User {username} ({role}) - {email}>'

    def __str__(self):
        return f"{self.get_full_name()} (@{self.username})"
