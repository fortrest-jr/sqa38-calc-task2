"""
Тесты для API калькулятора с использованием Hamcrest матчеров.
Создано для демонстрации техдолга на мастер-классе SQA Days 38.
"""

import pytest
import json
from hamcrest import (
    assert_that,
    equal_to,
    is_,
    close_to,
    has_length,
    instance_of,
    contains_string,
    greater_than,
    less_than,
    any_of,
    has_entry,
    has_entries,
    has_key,
    empty,
    not_none,
    starts_with,
    ends_with,
)


class TestCalculatorAPI:
    """Тесты для API калькулятора."""

    def test_health_check(self, client):
        """Тест проверки работоспособности API."""
        response = client.get('/api/health')
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data, has_entry('status', 'ok'))
        assert_that(data, has_entry('message', contains_string('Калькулятор')))
        assert_that(data, has_entries({'status': 'ok', 'message': contains_string('Калькулятор')}))

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (2, 3, 5),  # положительные числа
            (-1, 5, 4),  # отрицательное и положительное
            (0, 0, 0),  # нули
            (999999, 1, 1000000),  # большие числа
            (-5, -3, -8),  # отрицательные числа
        ],
    )
    def test_add_operation(self, client, a, b, expected):
        """Тест операции сложения с различными параметрами."""
        response = client.post('/api/add', data=json.dumps({'a': a, 'b': b}), content_type='application/json')
        assert_that(response.status_code, is_(200))
        data = json.loads(response.data)
        assert_that(
            data, has_entries({'operation': equal_to('add'), 'a': is_(a), 'b': is_(b), 'result': equal_to(expected)})
        )
        assert_that(data['result'], any_of(instance_of(int), instance_of(float)))

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (5, 3, 2),  # положительные числа
            (5, -3, 8),  # вычитание отрицательного
            (0, 0, 0),  # нули
            (1000000, 1, 999999),  # большие числа
            (-5, -3, -2),  # отрицательные числа
        ],
    )
    def test_subtract_operation(self, client, a, b, expected):
        """Тест операции вычитания с различными параметрами."""
        response = client.post('/api/subtract', data=json.dumps({'a': a, 'b': b}), content_type='application/json')
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data, has_entry('operation', 'subtract'))
        assert_that(data, has_entry('a', a))
        assert_that(data, has_entry('b', b))
        assert_that(data, has_entry('result', equal_to(expected)))

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (4, 3, 12),  # положительные числа
            (-2, 5, -10),  # отрицательное и положительное
            (0, 100, 0),  # умножение на ноль
            (1000, 1000, 1000000),  # большие числа
            (-3, -4, 12),  # отрицательные числа
        ],
    )
    def test_multiply_operation(self, client, a, b, expected):
        """Тест операции умножения с различными параметрами."""
        response = client.post('/api/multiply', data=json.dumps({'a': a, 'b': b}), content_type='application/json')
        assert_that(response.status_code, is_(200))
        data = json.loads(response.data)
        assert_that(data, has_entries({'operation': 'multiply', 'a': a, 'b': b, 'result': expected}))
        assert_that(data['result'], is_(not_none()))

    @pytest.mark.parametrize(
        "a,b,expected",
        [
            (6, 2, 3),  # положительные числа
            (-10, 2, -5),  # отрицательное и положительное
            (0, 5, 0),  # деление нуля
            (1000000, 2, 500000),  # большие числа
            (-9, -3, 3),  # отрицательные числа
        ],
    )
    def test_divide_operation(self, client, a, b, expected):
        """Тест операции деления с различными параметрами."""
        response = client.post('/api/divide', data=json.dumps({'a': a, 'b': b}), content_type='application/json')
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data, has_entry('operation', equal_to('divide')))
        assert_that(data, has_entry('a', is_(a)))
        assert_that(data, has_entry('b', is_(b)))
        assert_that(data, has_entry('result', equal_to(expected)))

    def test_divide_by_zero(self, client):
        """Тест деления на ноль."""
        response = client.post('/api/divide', data=json.dumps({'a': 5, 'b': 0}), content_type='application/json')
        assert_that(response.status_code, is_(equal_to(400)))
        data = json.loads(response.data)
        assert_that(data, has_key('error'))
        assert_that(data['error'], contains_string('Деление на ноль'))

    def test_missing_parameters(self, client):
        """Тест отсутствующих параметров."""
        response = client.post('/api/add', data=json.dumps({'a': 2}), content_type='application/json')
        assert_that(response.status_code, is_(equal_to(400)))
        data = json.loads(response.data)
        assert_that(data, has_entry('error', contains_string('Требуются параметры a и b')))

    def test_invalid_json(self, client):
        """Тест некорректного JSON."""
        response = client.post('/api/add', data='invalid json', content_type='application/json')
        assert_that(response.status_code, is_(equal_to(500)))

    @pytest.mark.parametrize(
        "operation,a,b,expected", [('add', 1, 2, 3), ('add', -1, 5, 4), ('add', 0, 0, 0), ('add', 999999, 1, 1000000)]
    )
    def test_calculate_add_operation(self, client, operation, a, b, expected):
        """Тест операции сложения через универсальный endpoint."""
        response = client.post(
            '/api/calculate', data=json.dumps({'operation': operation, 'a': a, 'b': b}), content_type='application/json'
        )
        assert_that(response.status_code, is_(200))
        data = json.loads(response.data)
        assert_that(data, has_entry('result', equal_to(expected)))

    @pytest.mark.parametrize(
        "operation,a,b,expected",
        [('subtract', 5, 2, 3), ('subtract', 5, -2, 7), ('subtract', 0, 0, 0), ('subtract', 1000000, 1, 999999)],
    )
    def test_calculate_subtract_operation(self, client, operation, a, b, expected):
        """Тест операции вычитания через универсальный endpoint."""
        response = client.post(
            '/api/calculate', data=json.dumps({'operation': operation, 'a': a, 'b': b}), content_type='application/json'
        )
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data['result'], is_(equal_to(expected)))

    @pytest.mark.parametrize(
        "operation,a,b,expected",
        [('multiply', 4, 3, 12), ('multiply', -2, 5, -10), ('multiply', 0, 100, 0), ('multiply', 1000, 1000, 1000000)],
    )
    def test_calculate_multiply_operation(self, client, operation, a, b, expected):
        """Тест операции умножения через универсальный endpoint."""
        response = client.post(
            '/api/calculate', data=json.dumps({'operation': operation, 'a': a, 'b': b}), content_type='application/json'
        )
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data, has_entry('result', equal_to(expected)))

    @pytest.mark.parametrize(
        "operation,a,b,expected",
        [('divide', 6, 2, 3), ('divide', -10, 2, -5), ('divide', 0, 5, 0), ('divide', 1000000, 2, 500000)],
    )
    def test_calculate_divide_operation(self, client, operation, a, b, expected):
        """Тест операции деления через универсальный endpoint."""
        response = client.post(
            '/api/calculate', data=json.dumps({'operation': operation, 'a': a, 'b': b}), content_type='application/json'
        )
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data['result'], is_(equal_to(expected)))

    def test_invalid_operation(self, client):
        """Тест неподдерживаемой операции."""
        response = client.post(
            '/api/calculate', data=json.dumps({'operation': 'power', 'a': 2, 'b': 3}), content_type='application/json'
        )
        assert_that(response.status_code, is_(equal_to(400)))
        data = json.loads(response.data)
        assert_that(data, has_entry('error', contains_string('Неподдерживаемая операция')))

    def test_history_endpoints(self, client):
        """Тест работы с историей."""
        # Выполняем несколько операций
        client.post('/api/add', data=json.dumps({'a': 1, 'b': 2}), content_type='application/json')
        client.post('/api/multiply', data=json.dumps({'a': 3, 'b': 4}), content_type='application/json')

        # Получаем историю
        response = client.get('/api/history')
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)

        # Проверяем структуру мета-данных
        assert_that(data, has_key('meta'))
        assert_that(data['meta'], has_key('user'))
        assert_that(
            data['meta']['user'], has_entries({'id': 'calc-user-001', 'name': 'Calculator Service', 'role': 'system'})
        )
        assert_that(data['meta'], has_key('timestamps'))
        assert_that(data['meta']['timestamps'], has_key('request_id'))
        assert_that(data['meta']['timestamps'], has_key('created_at'))
        assert_that(data['meta'], has_key('status'))
        assert_that(
            data['meta']['status'],
            has_entries({'code': 'SUCCESS', 'message': contains_string('История получена успешно')}),
        )

        # Проверяем структуру данных
        assert_that(data, has_key('data'))
        assert_that(data['data'], has_key('history'))
        assert_that(data['data'], has_key('pagination'))
        assert_that(
            data['data']['pagination'],
            has_entries({'total': equal_to(2), 'page': equal_to(1), 'per_page': equal_to(50), 'has_more': is_(False)}),
        )

        # Проверяем элементы истории
        history = data['data']['history']
        assert_that(history, has_length(2))
        assert_that(history[0], has_key('id'))
        assert_that(history[0], has_key('operation'))
        assert_that(
            history[0]['operation'],
            has_entries(
                {
                    'expression': equal_to('1.0 + 2.0'),
                    'type': equal_to('add'),
                    'operands': has_entries({'a': equal_to(1.0), 'b': equal_to(2.0)}),
                }
            ),
        )
        assert_that(history[0], has_key('result'))
        assert_that(
            history[0]['result'],
            has_entries({'value': equal_to(3), 'formatted': equal_to('3'), 'precision': equal_to(0)}),
        )
        assert_that(history[0], has_key('metadata'))
        assert_that(history[0]['metadata'], has_key('session_id'))

        assert_that(
            history[1],
            has_entries(
                {
                    'id': equal_to(2),
                    'operation': has_entries(
                        {
                            'expression': equal_to('3.0 * 4.0'),
                            'type': equal_to('multiply'),
                            'operands': has_entries({'a': equal_to(3.0), 'b': equal_to(4.0)}),
                        }
                    ),
                    'result': has_entries(
                        {'value': equal_to(12), 'formatted': equal_to('12'), 'precision': equal_to(0)}
                    ),
                }
            ),
        )

        # Очищаем историю
        response = client.delete('/api/history')
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data, has_entry('message', contains_string('История очищена')))

        # Проверяем, что история пуста
        response = client.get('/api/history')
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data['data']['pagination']['total'], is_(equal_to(0)))
        assert_that(data['data']['history'], empty())

    def test_404_error(self, client):
        """Тест обработки 404 ошибки."""
        response = client.get('/api/nonexistent')
        assert_that(response.status_code, is_(equal_to(404)))
        data = json.loads(response.data)
        assert_that(data, has_entry('error', contains_string('Endpoint не найден')))

    def test_method_not_allowed(self, client):
        """Тест обработки 405 ошибки."""
        response = client.get('/api/add')
        assert_that(response.status_code, is_(equal_to(405)))
        data = json.loads(response.data)
        assert_that(data, has_entry('error', contains_string('Метод не поддерживается')))

    def test_large_numbers(self, client):
        """Тест работы с очень большими числами."""
        # Максимальное 32-битное целое число
        max_int = 2**31 - 1
        response = client.post(
            '/api/add', data=json.dumps({'a': max_int, 'b': max_int}), content_type='application/json'
        )
        assert_that(response.status_code, is_(equal_to(200)))
        data = json.loads(response.data)
        assert_that(data['result'], is_(equal_to(max_int * 2)))

    def test_invalid_data_types(self, client):
        """Тест некорректных типов данных."""
        response = client.post('/api/add', data=json.dumps({'a': 'string', 'b': 2}), content_type='application/json')
        assert_that(response.status_code, is_(equal_to(400)))
        data = json.loads(response.data)
        assert_that(data, has_entry('error', contains_string('could not convert string to float')))

    def test_empty_request(self, client):
        """Тест пустого запроса."""
        response = client.post('/api/add', data='{}', content_type='application/json')
        assert_that(response.status_code, is_(equal_to(400)))
        data = json.loads(response.data)
        assert_that(data, has_entry('error', contains_string('Требуются параметры a и b')))

    def test_response_structure(self, client):
        """Тест структуры ответа API."""
        response = client.post('/api/add', data=json.dumps({'a': 5, 'b': 3}), content_type='application/json')
        data = json.loads(response.data)

        # Проверяем наличие всех ключей
        assert_that(data, has_key('operation'))
        assert_that(data, has_key('a'))
        assert_that(data, has_key('b'))
        assert_that(data, has_key('result'))

        # Проверяем типы значений
        assert_that(data['operation'], instance_of(str))
        assert_that(data['a'], any_of(instance_of(int), instance_of(float)))
        assert_that(data['b'], any_of(instance_of(int), instance_of(float)))
        assert_that(data['result'], any_of(instance_of(int), instance_of(float)))

    def test_float_precision(self, client):
        """Тест точности вычислений с плавающей точкой."""
        response = client.post('/api/divide', data=json.dumps({'a': 1, 'b': 3}), content_type='application/json')
        data = json.loads(response.data)
        assert_that(data['result'], close_to(0.333333, 0.000001))
        assert_that(data['result'], greater_than(0))
        assert_that(data['result'], less_than(1))

    def test_negative_results(self, client):
        """Тест отрицательных результатов."""
        response = client.post('/api/subtract', data=json.dumps({'a': 3, 'b': 5}), content_type='application/json')
        data = json.loads(response.data)
        assert_that(data['result'], less_than(0))
        assert_that(data['result'], equal_to(-2))

    def test_content_type_header(self, client):
        """Тест заголовка Content-Type."""
        response = client.post('/api/add', data=json.dumps({'a': 1, 'b': 2}), content_type='application/json')
        assert_that(response.content_type, contains_string('application/json'))

    def test_multiple_operations_sequence(self, client):
        """Тест последовательности нескольких операций."""
        operations = [('add', 10, 5, 15), ('subtract', 10, 5, 5), ('multiply', 10, 5, 50), ('divide', 10, 5, 2)]

        for op, a, b, expected in operations:
            response = client.post(
                '/api/calculate', data=json.dumps({'operation': op, 'a': a, 'b': b}), content_type='application/json'
            )
            data = json.loads(response.data)
            assert_that(data['result'], is_(equal_to(expected)))

    def test_history_order(self, client):
        """Тест порядка записей в истории."""
        client.post('/api/add', data=json.dumps({'a': 1, 'b': 1}), content_type='application/json')
        client.post('/api/add', data=json.dumps({'a': 2, 'b': 2}), content_type='application/json')
        client.post('/api/add', data=json.dumps({'a': 3, 'b': 3}), content_type='application/json')

        response = client.get('/api/history')
        data = json.loads(response.data)

        history = data['data']['history']
        assert_that(history, has_length(3))
        assert_that(history[0]['result']['value'], is_(equal_to(2)))
        assert_that(history[1]['result']['value'], is_(equal_to(4)))
        assert_that(history[2]['result']['value'], is_(equal_to(6)))

    def test_zero_division_error_message(self, client):
        """Тест сообщения об ошибке деления на ноль."""
        response = client.post('/api/divide', data=json.dumps({'a': 10, 'b': 0}), content_type='application/json')
        data = json.loads(response.data)
        assert_that(data['error'], starts_with('Деление на ноль'))
        assert_that(data['error'], ends_with('невозможно'))

    def test_calculate_endpoint_structure(self, client):
        """Тест структуры универсального endpoint."""
        response = client.post(
            '/api/calculate', data=json.dumps({'operation': 'add', 'a': 5, 'b': 3}), content_type='application/json'
        )
        data = json.loads(response.data)

        assert_that(data, has_entries({'operation': 'add', 'a': 5, 'b': 3, 'result': 8}))
