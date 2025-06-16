from flask import Flask, jsonify, request, abort
from app.models.amenity import Amenity

app = Flask(__name__)

# Stockage temporaire en mémoire
amenities = {}

# Helper pour retrouver une amenity
def get_amenity_or_404(amenity_id):
    amenity = amenities.get(amenity_id)
    if amenity is None or getattr(amenity, "_deleted", False):
        abort(404, description="Amenity not found")
    return amenity

# GET /amenities — Liste toutes les amenities
@app.route('/amenities', methods=['GET'])
def get_amenities():
    return jsonify([a.to_dict() for a in amenities.values() if not getattr(a, "_deleted", False)])

# GET /amenities/<id> — Détail d’une amenity
@app.route('/amenities/<amenity_id>', methods=['GET'])
def get_amenity(amenity_id):
    amenity = get_amenity_or_404(amenity_id)
    return jsonify(amenity.to_dict())

# POST /amenities — Créer une amenity
@app.route('/amenities', methods=['POST'])
def create_amenity():
    data = request.get_json()
    name = data.get('name')
    if not name:
        abort(400, description="Missing name")
    amenity = Amenity.create(name)
    amenities[str(amenity.id)] = amenity
    return jsonify(amenity.to_dict()), 201

# PUT /amenities/<id> — Modifier une amenity
@app.route('/amenities/<amenity_id>', methods=['PUT'])
def update_amenity(amenity_id):
    amenity = get_amenity_or_404(amenity_id)
    data = request.get_json()
    name = data.get('name')
    if name:
        amenity.update(name=name)
    return jsonify(amenity.to_dict())

# DELETE /amenities/<id> — Supprimer une amenity
@app.route('/amenities/<amenity_id>', methods=['DELETE'])
def delete_amenity(amenity_id):
    amenity = get_amenity_or_404(amenity_id)
    amenity.delete()
    return jsonify({"result": True})

if __name__ == "__main__":
    from flask import Flask
    app.run(debug=True)
