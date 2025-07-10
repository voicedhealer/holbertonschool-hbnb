import uuid

class MemoryRepository:
    """Un repository générique en mémoire pour toutes les entités."""

    def __init__(self):
        self._storage = {}

    def add(self, obj):
        # On suppose que l'objet a un attribut 'id' (string, UUID)
        if not hasattr(obj, 'id') or not obj.id:
            obj.id = str(uuid.uuid4())
        self._storage[obj.id] = obj
        return obj

    def get(self, obj_id):
        return self._storage.get(obj_id)

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if not obj:
            return None
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        for obj in self._storage.values():
            if hasattr(obj, attr_name) and getattr(obj, attr_name) == attr_value:
                return obj
        return None

    def filter_by_attribute(self, attr_name, attr_value):
        return [
            obj for obj in self._storage.values()
            if hasattr(obj, attr_name) and getattr(obj, attr_name) == attr_value
        ]
