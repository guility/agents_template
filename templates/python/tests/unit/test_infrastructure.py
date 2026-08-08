"""Unit tests для infrastructure layer."""

import pytest
from src.infrastructure import InMemoryRepository
from src.domain import Entity


class TestInMemoryRepository:
    """Тесты для InMemoryRepository."""
    
    @pytest.fixture
    def repository(self):
        return InMemoryRepository()
    
    @pytest.fixture
    def test_entity(self):
        return Entity(id="test-1")
    
    def test_save_entity(self, repository, test_entity):
        """Сохранение сущности."""
        saved = repository.save(test_entity)
        assert saved.id == "test-1"
    
    def test_get_by_id_existing(self, repository, test_entity):
        """Получение существующей сущности."""
        repository.save(test_entity)
        found = repository.get_by_id("test-1")
        assert found is not None
        assert found.id == "test-1"
    
    def test_get_by_id_not_existing(self, repository):
        """Получение несуществующей сущности."""
        found = repository.get_by_id("nonexistent")
        assert found is None
    
    def test_get_all(self, repository, test_entity):
        """Получение всех сущностей."""
        repository.save(test_entity)
        entity2 = Entity(id="test-2")
        repository.save(entity2)
        
        all_entities = repository.get_all()
        assert len(all_entities) == 2
    
    def test_delete_existing(self, repository, test_entity):
        """Удаление существующей сущности."""
        repository.save(test_entity)
        result = repository.delete("test-1")
        assert result is True
        assert repository.get_by_id("test-1") is None
    
    def test_delete_not_existing(self, repository):
        """Удаление несуществующей сущности."""
        result = repository.delete("nonexistent")
        assert result is False
