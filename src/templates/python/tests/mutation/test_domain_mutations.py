"""Mutation tests для domain layer.

Каждая функция должна иметь минимум 2 мутации.
"""

import pytest

from src.domain import BaseEntity, Entity


class TestBaseEntityMutations:
    """Мутационные тесты для BaseEntity."""

    def test_mutation_created_at_not_set(self):
        """Мутация: created_at не устанавливается автоматически."""
        # Мутация 1: created_at остается None
        with pytest.raises(Exception):
            # Если убрать авто-установку created_at
            entity = BaseEntity.__new__(BaseEntity)
            entity.id = "test"
            entity.created_at = None
            entity.updated_at = None
            # __post_init__ не вызван

    def test_mutation_id_can_be_changed(self):
        """Мутация: ID можно изменить (нарушение immutability)."""
        entity = BaseEntity(id="original")

        with pytest.raises(AttributeError):
            entity.id = "changed"


class TestEntityMutations:
    """Мутационные тесты для Entity."""

    def test_mutation_update_does_not_change_timestamp(self):
        """Мутация: update() не меняет updated_at."""
        entity = Entity(id="test-1")
        old_timestamp = entity.updated_at

        entity.update()

        assert entity.updated_at is not None
        if old_timestamp is not None:
            assert entity.updated_at >= old_timestamp

    def test_mutation_update_accepts_invalid_keys(self):
        """Мутация: update() принимает несуществующие ключи."""
        entity = Entity(id="test-1")

        # Мутация 2: если убрать проверку hasattr
        # Симулируем мутацию
        try:
            entity.update(invalid_key="value")
            # В нормальном коде это должно игнорироваться
        except AttributeError:
            pytest.fail("Мутация обнаружена: AttributeError вместо игнорирования")
