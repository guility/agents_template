"""Domain layer - бизнес-сущности и логика предметной области."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class BaseEntity:
    """Базовый класс для всех сущностей домена."""
    id: str
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.now())


@dataclass(frozen=True)
class ValueObject:
    """Базовый класс для объектов-значений (неизменяемы)."""
    pass


@dataclass
class Entity(BaseEntity):
    """Базовая сущность с поведением."""
    
    def update(self, **kwargs):
        """Обновление сущности."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                object.__setattr__(self, key, value)
        object.__setattr__(self, 'updated_at', datetime.now())
