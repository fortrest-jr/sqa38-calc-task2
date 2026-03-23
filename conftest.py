"""
Общие pytest фикстуры для всех тестов проекта.
"""

import pytest
import tempfile
from calculator import Calculator
from app import create_app


@pytest.fixture
def calculator():
    """
    Фикстура для создания калькулятора с временным файлом истории.
    Используется в test_calculator.py и test_api.py.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        # Создаем калькулятор с временным файлом истории
        calc = Calculator()
        calc.history_file = temp_file.name
        calc.history = []

        yield calc


@pytest.fixture
def client(calculator):
    """
    Создание тестового клиента Flask с изолированной историей.
    Использует общую фикстуру calculator для изоляции состояния.
    """
    app = create_app()
    app.config['TESTING'] = True

    # Используем калькулятор из фикстуры
    app.calculator = calculator

    with app.test_client() as client:
        yield client
