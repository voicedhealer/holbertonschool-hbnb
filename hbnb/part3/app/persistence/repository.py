from abc import ABC, abstractmethod
from .repository import Repository
from app import db
from app.models.user import User 

class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, obj_id, data):
        pass

    @abstractmethod
    def delete(self, obj_id):
        pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value):
        pass


class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}

    def add(self, obj):
        self._storage[obj.id] = obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(data)

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value), None)

class UserRepository(Repository):
    def add(self, obj):
        db.session.add(obj) # On ajoute à la session
        db.session.commit() # On confirme/enregistre en base de données

    def get(self, obj_id):
        return db.session.get(User, obj_id)

    def get_all(self):
        return User.query.all()

    def update(self, obj_id, data):
        user = self.get(obj_id)
        if user:
            user.update(data)
            db.session.commit()

    def delete(self, obj_id):
        user = self.get(obj_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def get_by_attribute(self, attr_name, attr_value):
        return User.query.filter(getattr(User, attr_name) == attr_value).first()
