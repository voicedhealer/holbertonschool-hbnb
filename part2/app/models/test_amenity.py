from amenity import Amenity  # adapte si ta classe est dans un autre fichier

# Création d'une commodité
wifi = Amenity.create("WiFi")
print("Après création :", wifi.to_dict())

# Mise à jour du nom
wifi.update(name="Wi-Fi Haut Débit")
print("Après update :", wifi.to_dict())
