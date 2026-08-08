"""Application layer - use cases и порты (интерфейсы)."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List


T = TypeVar('T')


class RepositoryPort(ABC, Generic[T]):
    """Порт для репозиториев (контракт инфраструктуры)."""
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Получение сущности по ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """Получение всех сущностей."""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Сохранение сущности."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Удаление сущности."""
        pass


class UseCase(ABC, Generic[T]):
    """Базовый класс для use case."""
    
    @abstractmethod
    def execute(self, **kwargs) -> T:
        """Выполнение use case."""
        pass
