"""Integration tests для репозиториев."""

import pytest

from src.domain import Entity
from src.infrastructure import InMemoryRepository


class TestRepositoryIntegration:
    """Интеграционные тесты репозитория."""

    @pytest.fixture
    def repository(self):
        return InMemoryRepository()

    def test_full_crud_lifecycle(self, repository):
        """Полный CRUD жизненный цикл."""
        # Create
        entity = Entity(id="entity-1")
        saved = repository.save(entity)
        assert saved.id == "entity-1"

        # Read
        found = repository.get_by_id("entity-1")
        assert found is not None
        assert found.id == "entity-1"

        # Update (через save)
        updated = repository.save(found)
        assert updated is not None

        # Delete
        deleted = repository.delete("entity-1")
        assert deleted is True

        # Verify deletion
        not_found = repository.get_by_id("entity-1")
        assert not_found is None

    def test_multiple_entities_isolation(self, repository):
        """Изоляция множественных сущностей."""
        entities = [Entity(id=f"entity-{i}") for i in range(5)]

        for entity in entities:
            repository.save(entity)

        all_entities = repository.get_all()
        assert len(all_entities) == 5

        # Удаление одной не влияет на другие
        repository.delete("entity-2")
        remaining = repository.get_all()
        assert len(remaining) == 4
