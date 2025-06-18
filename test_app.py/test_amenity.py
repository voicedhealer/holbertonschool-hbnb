from part2.app.models.amenity import Amenity

# Création d'une commodité
wifi = Amenity.create("WiFi")
print("Après création :", wifi.to_dict())

# Mise à jour du nom
wifi.update(name="Wi-Fi Haut Débit")
print("Après update :", wifi.to_dict())
