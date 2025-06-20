from abc import ABC, abstractmethod
import uuid
from typing import List, Any

class Repository(ABC):
    @abstractmethod
    def add(self, obj):
        pass

    @abstractmethod
    def get(self, obj_id):
        pass

    @abstractmethod
    def get_all(self) -> list:
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

    def get_all(self) -> list:
        return list(self._storage.values())
    
    def create(self, obj):
        if not hasattr(obj, 'id'):
            obj.id = str(uuid.uuid4())
        self._storage[obj.id] = obj
        return obj

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(**data)
            return obj
        return None

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        return next((obj for obj in self._storage.values() if getattr(obj, attr_name) == attr_value), None)
    
    def clear(self):
        self._storage = {}