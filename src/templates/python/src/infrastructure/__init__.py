"""Infrastructure layer - реализация портов."""

from typing import Optional, List, Dict
from src.application import RepositoryPort


class InMemoryRepository(RepositoryPort):
    """In-memory реализация репозитория (для тестов)."""
    
    def __init__(self):
        self._storage: Dict[str, any] = {}
    
    def get_by_id(self, id: str) -> Optional[any]:
        return self._storage.get(id)
    
    def get_all(self) -> List[any]:
        return list(self._storage.values())
    
    def save(self, entity: any) -> any:
        self._storage[entity.id] = entity
        return entity
    
    def delete(self, id: str) -> bool:
        if id in self._storage:
            del self._storage[id]
            return True
        return False
