# 🏠 HBnB - Part 3: Authentication, Persistence, and ER Diagrams

Troisième partie du projet ""HBnB"", application web inspirée d'Airbnb. Cette étape se concentre sur :

- 🔒 L'authentification des utilisateurs (JWT)
- 🧠 La gestion des rôles (utilisateur vs administrateur)
- 💾 La persistance des données avec SQLAlchemy
- 🗺️ La modélisation visuelle de la base de données (ER Diagram via Mermaid.js)

---

## 🧩 Objectifs principaux

| Tâche | Description | Statut |
|------|-------------|--------|
| 0 | Configuration de l'Application Factory
| 1 | Hashage du mot de passe utilisateur avec Bcrypt
| 2 | Authentification avec JWT (flask-jwt-extended)
| 3 | Accès protégé pour les utilisateurs authentifiés
| 4 | Accès administrateur pour endpoints critiques
| 5 | Passage à SQLAlchemy pour la persistance
| 6 | Mapping de l'entité `User`
| 7 | Mapping de `Place`, `Review`, `Amenity`
| 8 | Relations entre entités (`1:N`, `N:N`)
| 9 | SQL brut : création de tables & données initiales
| 10 | Génération d’un diagramme ER avec Mermaid.js

---

## 🗃️ Structure du Projet
```
holbertonschool-hbnb/
hbnb/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       ├── amenities.py
│   │       └── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── amenity.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   ├── memory_repository.py
│   │   └── sqlalchemy_repository.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── place_repository.py
│   │   ├── amenity_repository.py
│   │   └── review_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── facade.py
│   │   └── auth.py 
│   ├── tests/
│       ├── __init__.py
│       ├── test_users.py
│       ├── test_places.py
│       ├── test_amenities.py
│       └── test_reviews.py
├── run.py
├── config.py
├── requirements.txt
├── extensions.py
├── erDiagram.mmd
├── init_admin.py
├── README.md
```

## ⚙️ Technologies Utilisées

- **Python 3.12+**
- **Flask**
- **Flask-RESTx**
- **Flask-Bcrypt**
- **Flask-JWT-Extended**
- **Flask-SQLAlchemy**
- **Werkzeug**
- **Mermaid.js** (pour les ER diagrams)
- **cURL / Postman** (pour tester l’API)

---

## 🔐 Authentification

Les utilisateurs peuvent :
- S’inscrire avec un mot de passe hashé
- Se connecter pour obtenir un **token JWT**
- Accéder à des routes protégées via le header :

Les administrateurs peuvent :
- Créer / modifier n’importe quel utilisateur
- Ajouter des amenities
- Bypasser les règles de propriété (`ownership`)

---

## 🧱 Base de Données

Les entités principales sont :

- `User` 👤
- `Place` 🏠
- `Review` ✍️
- `Amenity` 🛁
- `Place_Amenity` (table d’association) 🔗

👉 Voir le fichier [`erDiagram.mmd`](./erDiagram.mmd) pour le schéma complet.

---

## 🚀 Lancer l’application

```
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer un shell Flask pour initier la base
flask shell
>>> from app import db
>>> db.create_all()

# 3. Lancer le serveur
python3 run.py

📬 Points de terminaison API (exemples)
POST /api/v1/users/ : Créer un utilisateur

POST /api/v1/auth/login : Connexion & token JWT

GET /api/v1/places/ : Liste des places (public)

POST /api/v1/reviews/ : Ajouter un avis (protégé)


TEST API AVEC CURL
# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
 -H "Content-Type: application/json" \
 -d '{"email": "admin@hbnb.io", "password": "admin1234"}'

# Accès protégé
curl -H "Authorization: Bearer <votre_token>" \
 http://localhost:5000/api/v1/users/me
```

## ✍️ Auteurs :
[Choisy Anaïs](https://github.com/o0anais0o)
[Patricia Bagashvili](https://github.com/alizium)
[Vivien Bernardot](https://github.com/voicedhealer)
