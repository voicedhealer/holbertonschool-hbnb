from app import db

class Amenity(db.Model):
    __tablename__ = 'amenities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if name is None or len(name) == 0:
            raise ValueError("Name is required.")
        if len(name) > 50:
            raise ValueError("Name must be 50 characters max.")
        self.name = name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def __repr__(self):
        return f'<Amenity {self.name}>'
