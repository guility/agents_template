"""Application layer - use cases и порты (интерфейсы)."""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class RepositoryPort(ABC, Generic[T]):
    """Порт для репозиториев (контракт инфраструктуры)."""

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Получение сущности по ID."""
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        """Получение всех сущностей."""
        raise NotImplementedError

    @abstractmethod
    def save(self, entity: T) -> T:
        """Сохранение сущности."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Удаление сущности."""
        raise NotImplementedError


class UseCase(ABC, Generic[T]):
    """Базовый класс для use case."""

    @abstractmethod
    def execute(self, **kwargs) -> T:
        """Выполнение use case."""
        raise NotImplementedError
