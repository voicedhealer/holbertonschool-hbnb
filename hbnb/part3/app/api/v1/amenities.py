from flask_restx import Namespace, Resource, fields
from flask import request
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('amenities', description='Amenity operations')

# Modèle pour la documentation et la validation
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Nom de l\'équipement')
})

# --- Endpoints réservés aux admins ---

@api.route('/amenities/')
class AmenityAdminCreate(Resource):
    @api.expect(amenity_model)
    @jwt_required()
    def post(self):
        """Créer un nouvel équipement (admin uniquement)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload or request.json
        existing_amenity = facade.amenity_repo.get_by_attribute('name', amenity_data.get('name'))
        if existing_amenity:
            return {'error': 'Amenity already exists'}, 400
        try:
            new_amenity = facade.create_amenity(amenity_data)
            return new_amenity.to_dict(), 201
        except Exception as e:
            return {'error': str(e)}, 400

@api.route('/amenities/<amenity_id>')
class AmenityAdminUpdate(Resource):
    @api.expect(amenity_model)
    @jwt_required()
    def put(self, amenity_id):
        """Modifier un équipement (admin uniquement)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        amenity_data = api.payload or request.json
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        try:
            facade.update_amenity(amenity_id, amenity_data)
            return {"message": "Amenity updated successfully"}, 200
        except Exception as e:
            return {'error': str(e)}, 400

# --- Endpoints publics (lecture seule) ---

@api.route('/amenities/')
class AmenityList(Resource):
    @api.response(200, 'Liste des équipements récupérée avec succès')
    def get(self):
        """Récupérer la liste de tous les équipements (public)"""
        amenities = facade.get_all_amenities()
        return [amenity.to_dict() for amenity in amenities], 200

@api.route('/amenities/<amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Détails de l\'équipement récupérés avec succès')
    @api.response(404, 'Équipement non trouvé')
    def get(self, amenity_id):
        """Obtenir les détails d'un équipement par son ID (public)"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        return amenity.to_dict(), 200
