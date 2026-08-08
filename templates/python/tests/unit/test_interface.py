"""Unit tests для interface layer."""

import pytest
from src.interface import ResponseDTO


class TestResponseDTO:
    """Тесты для ResponseDTO."""
    
    def test_create_success_response(self):
        """Создание успешного ответа."""
        response = ResponseDTO.ok(data={"key": "value"})
        assert response.success is True
        assert response.data == {"key": "value"}
        assert response.error is None
    
    def test_create_fail_response(self):
        """Создание ответа с ошибкой."""
        response = ResponseDTO.fail(error="Something went wrong")
        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.data is None
    
    def test_to_dict_success(self):
        """Конверсия успешного ответа в dict."""
        response = ResponseDTO.ok(data={"result": 42})
        result = response.to_dict()
        assert result == {
            'success': True,
            'data': {'result': 42},
            'error': None
        }
    
    def test_to_dict_fail(self):
        """Конверсия ответа с ошибкой в dict."""
        response = ResponseDTO.fail(error="Error message")
        result = response.to_dict()
        assert result == {
            'success': False,
            'data': None,
            'error': 'Error message'
        }
    
    def test_default_values(self):
        """Значения по умолчанию."""
        response = ResponseDTO(success=True)
        assert response.data is None
        assert response.error is None
