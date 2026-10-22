"""Unit tests для application layer."""

import pytest
from src.application import RepositoryPort, UseCase


class MockEntity:
    """Mock сущность для тестов."""
    def __init__(self, id: str):
        self.id = id


class TestRepositoryPort:
    """Тесты для RepositoryPort."""
    
    def test_repository_port_is_abstract(self):
        """RepositoryPort - абстрактный класс."""
        with pytest.raises(TypeError):
            RepositoryPort()
    
    def test_repository_port_methods_are_abstract(self):
        """Методы RepositoryPort абстрактные."""
        assert hasattr(RepositoryPort, 'get_by_id')
        assert hasattr(RepositoryPort, 'get_all')
        assert hasattr(RepositoryPort, 'save')
        assert hasattr(RepositoryPort, 'delete')


class TestUseCase:
    """Тесты для UseCase."""
    
    def test_use_case_is_abstract(self):
        """UseCase - абстрактный класс."""
        with pytest.raises(TypeError):
            UseCase()
    
    def test_use_case_has_execute_method(self):
        """UseCase имеет метод execute."""
        assert hasattr(UseCase, 'execute')


class ConcreteUseCase(UseCase):
    """Concrete implementation для тестов."""
    def execute(self, **kwargs):
        return kwargs.get('value', 'default')


class TestConcreteUseCase:
    """Тесты для конкретной реализации UseCase."""
    
    def test_execute_returns_value(self):
        """execute возвращает значение."""
        use_case = ConcreteUseCase()
        result = use_case.execute(value="test")
        assert result == "test"
    
    def test_execute_default_value(self):
        """execute возвращает default при отсутствии аргументов."""
        use_case = ConcreteUseCase()
        result = use_case.execute()
        assert result == "default"
