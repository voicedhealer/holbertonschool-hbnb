-- Supprimer les tables si elles existent déjà
DROP TABLE IF EXISTS place_amenity;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS amenities;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS app_users;

-- Table app_users (User)
CREATE TABLE app_users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    role VARCHAR(80) DEFAULT 'user' NOT NULL
);

-- Table places (Place)
CREATE TABLE places (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    owner_id CHAR(36) NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES app_users(id) ON DELETE CASCADE
);

-- Table amenities (Amenity)
CREATE TABLE amenities (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

-- Table place_amenity (many-to-many)
CREATE TABLE place_amenity (
    place_id CHAR(36) NOT NULL,
    amenity_id CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
);

-- Table reviews (Review)
CREATE TABLE reviews (
    id CHAR(36) PRIMARY KEY,
    text TEXT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    place_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES app_users(id) ON DELETE CASCADE,
    UNIQUE (user_id, place_id)
);

-- Insertion de l’utilisateur admin (UUID fixe)
INSERT INTO app_users (
    id, username, password, first_name, last_name, email, is_admin, role
) VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'admin',
    '$2b$12$yJz7VjQkIEBXJ8w9WyE4kuCHphs1kA7bi1XxO/U1duWcyMoxevywa',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    TRUE,
    'admin'
);

-- Insertion des 3 amenities (avec UUID4)
INSERT INTO amenities (id, name) VALUES
('9e98d697-d2d8-4873-8d67-79d20de3708e', 'WiFi'),
('8e3b0d99-1f3e-4db6-8887-d02a9b719be3', 'Swimming Pool'),
('48b52736-d929-4f3d-9b34-08a5ee8f5bb3', 'Air Conditioning');
