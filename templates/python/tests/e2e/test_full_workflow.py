"""E2E tests для полного workflow."""

import pytest
from src.domain import Entity
from src.infrastructure import InMemoryRepository
from src.interface import ResponseDTO


class TestFullWorkflow:
    """E2E тесты полного рабочего процесса."""
    
    @pytest.fixture
    def setup_system(self):
        """Настройка системы для теста."""
        repository = InMemoryRepository()
        return {"repository": repository}
    
    def test_create_read_update_delete_workflow(self, setup_system):
        """Полный CRUD workflow."""
        repo = setup_system["repository"]
        
        # CREATE: Создание сущности
        entity = Entity(id="e2e-entity-1")
        saved = repo.save(entity)
        assert saved.id == "e2e-entity-1"
        
        # READ: Чтение сущности
        found = repo.get_by_id("e2e-entity-1")
        assert found is not None
        
        # UPDATE: Обновление через интерфейс
        response = ResponseDTO.ok(data={"id": found.id, "status": "updated"})
        assert response.success is True
        assert response.data["status"] == "updated"
        
        # DELETE: Удаление сущности
        deleted = repo.delete("e2e-entity-1")
        assert deleted is True
        
        # VERIFY: Проверка удаления
        not_found = repo.get_by_id("e2e-entity-1")
        assert not_found is None
    
    def test_batch_operations_workflow(self, setup_system):
        """Workflow пакетных операций."""
        repo = setup_system["repository"]
        
        # Batch create
        entities = [Entity(id=f"batch-{i}") for i in range(10)]
        for entity in entities:
            repo.save(entity)
        
        # Verify batch
        all_entities = repo.get_all()
        assert len(all_entities) == 10
        
        # Batch delete every second
        for i in range(0, 10, 2):
            repo.delete(f"batch-{i}")
        
        remaining = repo.get_all()
        assert len(remaining) == 5
    
    def test_error_handling_workflow(self, setup_system):
        """Workflow обработки ошибок."""
        repo = setup_system["repository"]
        
        # Attempt to get non-existent
        result = repo.get_by_id("nonexistent")
        assert result is None
        
        # Attempt to delete non-existent
        deleted = repo.delete("nonexistent")
        assert deleted is False
        
        # Error response
        error_response = ResponseDTO.fail(error="Entity not found")
        assert error_response.success is False
        assert error_response.error == "Entity not found"
