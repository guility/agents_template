"""Unit tests для domain layer."""

import pytest
from datetime import datetime
from src.domain import BaseEntity, ValueObject, Entity


class TestBaseEntity:
    """Тесты для BaseEntity."""
    
    def test_create_entity_with_id(self):
        """Создание сущности с ID."""
        entity = BaseEntity(id="test-123")
        assert entity.id == "test-123"
    
    def test_entity_created_at_auto_set(self):
        """created_at устанавливается автоматически."""
        entity = BaseEntity(id="test-123")
        assert entity.created_at is not None
        assert isinstance(entity.created_at, datetime)
    
    def test_entity_is_immutable(self):
        """BaseEntity неизменяема (frozen)."""
        entity = BaseEntity(id="test-123")
        with pytest.raises(AttributeError):
            entity.id = "new-id"


class TestValueObject:
    """Тесты для ValueObject."""
    
    def test_value_object_creation(self):
        """Создание объекта-значения."""
        vo = ValueObject()
        assert vo is not None
    
    def test_value_object_is_immutable(self):
        """ValueObject неизменяем (frozen)."""
        vo = ValueObject()
        with pytest.raises(AttributeError):
            vo.new_attr = "value"


class TestEntity:
    """Тесты для Entity."""
    
    def test_entity_creation(self):
        """Создание сущности."""
        entity = Entity(id="entity-1")
        assert entity.id == "entity-1"
        assert entity.created_at is not None
    
    def test_entity_update(self):
        """Обновление сущности."""
        entity = Entity(id="entity-1")
        old_updated_at = entity.updated_at
        
        # Обновление должно изменить updated_at
        entity.update()
        
        assert entity.updated_at is not None
        if old_updated_at:
            assert entity.updated_at >= old_updated_at
    
    def test_entity_inherits_from_base(self):
        """Entity наследуется от BaseEntity."""
        entity = Entity(id="entity-1")
        assert isinstance(entity, BaseEntity)
