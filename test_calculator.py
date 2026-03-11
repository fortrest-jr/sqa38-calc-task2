"""
Тесты для калькулятора в формате pytest с использованием Hamcrest матчеров.
Создано для демонстрации техдолга на мастер-классе SQA Days 38.
"""

import pytest
import tempfile
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    close_to,
    has_length,
    instance_of,
    contains_exactly,
    contains_string,
    greater_than,
    less_than,
    all_of,
    any_of,
    has_item,
    empty,
    not_none,
    same_instance,
    calling,
    raises,
)
from calculator import Calculator


@pytest.fixture
def calculator():
    """Фикстура для создания калькулятора с временным файлом истории."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as temp_file:
        # Создаем калькулятор с временным файлом истории
        calc = Calculator()
        calc.history_file = temp_file.name
        calc.history = []

        yield calc


@pytest.mark.parametrize("a,b,expected", [(2, 3, 5), (-1, 1, 0), (0.5, 0.5, 1.0)])
def test_add(calculator, a, b, expected):
    """Тест сложения с параметризацией."""
    result = calculator.add(a, b)
    assert_that(result, is_(equal_to(expected)))
    assert_that(result, any_of(instance_of(int), instance_of(float)))


@pytest.mark.parametrize("a,b,expected", [(5, 3, 2), (1, 1, 0), (-1, 1, -2)])
def test_subtract(calculator, a, b, expected):
    """Тест вычитания с параметризацией."""
    result = calculator.subtract(a, b)
    assert_that(result, equal_to(expected))
    assert_that(result, is_(not_none()))


@pytest.mark.parametrize("a,b,expected", [(2, 3, 6), (-2, 3, -6), (0, 5, 0)])
def test_multiply(calculator, a, b, expected):
    """Тест умножения с параметризацией."""
    result = calculator.multiply(a, b)
    assert_that(result, is_(equal_to(expected)))
    assert_that(result, any_of(instance_of(int), instance_of(float)))


@pytest.mark.parametrize("a,b,expected", [(6, 2, 3.0), (5, 2, 2.5), (-6, 2, -3.0), (4, 3, 1.333333)])
def test_divide(calculator, a, b, expected):
    """Тест деления с параметризацией."""
    result = calculator.divide(a, b)
    assert_that(result, close_to(expected, 0.0001))
    assert_that(result, all_of(instance_of(float), greater_than(-1000), less_than(1000)))


def test_divide_by_zero(calculator):
    """Тест деления на ноль."""
    assert_that(calling(calculator.divide).with_args(5, 0), raises(ValueError, "Деление на ноль"))


def test_history_after_operations(calculator):
    """Тест истории после операций."""
    # Выполняем несколько операций
    calculator.add(2, 3)
    calculator.subtract(5, 1)
    calculator.multiply(4, 2)

    # Проверяем историю
    history = calculator.get_history()
    assert_that(history, has_length(3))
    assert_that(history, instance_of(list))

    # Проверяем каждую запись с разными матчерами
    assert_that(history[0], contains_exactly(equal_to("2 + 3"), equal_to(5)))
    assert_that(history[1], contains_exactly(is_("5 - 1"), is_(4)))
    assert_that(history[2], contains_exactly(equal_to("4 * 2"), equal_to(8)))


def test_clear_history(calculator):
    """Тест очистки истории."""
    # Добавляем операции
    calculator.add(1, 1)
    calculator.multiply(2, 3)

    assert_that(calculator.get_history(), has_length(2))

    # Очищаем историю
    calculator.clear_history()

    # Проверяем, что история пустая
    assert_that(calculator.get_history(), empty())
    assert_that(calculator.get_history(), has_length(0))


def test_history_persistence(calculator):
    """Тест сохранения истории в файл."""
    # Добавляем операции
    calculator.add(1, 2)
    calculator.multiply(3, 4)

    # Проверяем, что история содержит записи
    history = calculator.get_history()
    assert_that(history, has_length(2))
    assert_that(history, instance_of(list))

    # Проверяем типы элементов
    assert_that(history[0], instance_of(tuple))
    assert_that(history[1], instance_of(tuple))

    # Проверяем содержимое
    assert_that(history[0], contains_exactly(equal_to("1 + 2"), equal_to(3)))
    assert_that(history[1], contains_exactly(is_("3 * 4"), is_(12)))


def test_result_types(calculator):
    """Тест типов возвращаемых значений."""
    result = calculator.add(1, 2)
    assert_that(result, any_of(instance_of(int), instance_of(float)))

    result = calculator.divide(1, 2)
    assert_that(result, instance_of(float))
    assert_that(result, greater_than(0))
    assert_that(result, less_than(1))


def test_history_item_structure(calculator):
    """Тест структуры элементов истории."""
    calculator.add(5, 3)
    history = calculator.get_history()

    assert_that(history, has_length(1))
    assert_that(history[0], instance_of(tuple))
    assert_that(history[0], has_length(2))
    assert_that(history[0][0], instance_of(str))
    assert_that(history[0][1], any_of(instance_of(int), instance_of(float)))


def test_multiple_operations_sequence(calculator):
    """Тест последовательности нескольких операций."""
    results = []
    results.append(calculator.add(10, 5))
    results.append(calculator.subtract(10, 5))
    results.append(calculator.multiply(10, 5))
    results.append(calculator.divide(10, 5))

    assert_that(results, has_length(4))
    assert_that(results, contains_exactly(equal_to(15), equal_to(5), equal_to(50), equal_to(2.0)))


def test_negative_numbers(calculator):
    """Тест работы с отрицательными числами."""
    result = calculator.add(-5, -3)
    assert_that(result, less_than(0))
    assert_that(result, equal_to(-8))

    result = calculator.multiply(-2, 3)
    assert_that(result, less_than(0))
    assert_that(result, equal_to(-6))

    result = calculator.multiply(-2, -3)
    assert_that(result, greater_than(0))
    assert_that(result, equal_to(6))


def test_zero_operations(calculator):
    """Тест операций с нулём."""
    assert_that(calculator.add(0, 5), equal_to(5))
    assert_that(calculator.subtract(5, 0), equal_to(5))
    assert_that(calculator.multiply(0, 5), equal_to(0))
    assert_that(calculator.multiply(5, 0), equal_to(0))


if __name__ == '__main__':
    pytest.main([__file__])
