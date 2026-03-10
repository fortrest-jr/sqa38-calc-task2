"""
Flask веб-приложение с REST API для калькулятора.
"""

from flask import Flask, request, jsonify
from calculator import Calculator
from datetime import datetime, timezone
import uuid

app = Flask(__name__)

# Создаем глобальный экземпляр калькулятора
calculator = Calculator()

# Схема структуры ответа истории (для документации - неудобный формат для прямого использования в тестах)
# {
#     "meta": {
#         "user": {"id": str, "name": str, "role": str},
#         "timestamps": {"created_at": str, "timezone": str, "request_id": str},
#         "status": {"code": str, "message": str, "execution_time_ms": int}
#     },
#     "data": {
#         "history": [
#             {
#                 "id": int,
#                 "operation": {"expression": str, "type": str, "operands": {"a": float, "b": float}},
#                 "result": {"value": float, "formatted": str, "precision": int},
#                 "metadata": {"timestamp": str, "session_id": str}
#             }
#         ],
#         "pagination": {"total": int, "page": int, "per_page": int, "has_more": bool}
#     }
# }


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности API."""
    return jsonify({'status': 'ok', 'message': 'Калькулятор работает'})


@app.route('/api/add', methods=['POST'])
def add():
    """API endpoint для сложения."""
    try:
        data = request.get_json()
        if not data or 'a' not in data or 'b' not in data:
            return jsonify({'error': 'Требуются параметры a и b'}), 400

        a = float(data['a'])
        b = float(data['b'])
        result = calculator.add(a, b)

        return jsonify({'operation': 'add', 'a': a, 'b': b, 'result': result})
    except ValueError as e:
        return jsonify({'error': f'Некорректные данные: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/subtract', methods=['POST'])
def subtract():
    """API endpoint для вычитания."""
    try:
        data = request.get_json()
        if not data or 'a' not in data or 'b' not in data:
            return jsonify({'error': 'Требуются параметры a и b'}), 400

        a = float(data['a'])
        b = float(data['b'])
        result = calculator.subtract(a, b)

        return jsonify({'operation': 'subtract', 'a': a, 'b': b, 'result': result})
    except ValueError as e:
        return jsonify({'error': f'Некорректные данные: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/multiply', methods=['POST'])
def multiply():
    """API endpoint для умножения."""
    try:
        data = request.get_json()
        if not data or 'a' not in data or 'b' not in data:
            return jsonify({'error': 'Требуются параметры a и b'}), 400

        a = float(data['a'])
        b = float(data['b'])
        result = calculator.multiply(a, b)

        return jsonify({'operation': 'multiply', 'a': a, 'b': b, 'result': result})
    except ValueError as e:
        return jsonify({'error': f'Некорректные данные: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/divide', methods=['POST'])
def divide():
    """API endpoint для деления."""
    try:
        data = request.get_json()
        if not data or 'a' not in data or 'b' not in data:
            return jsonify({'error': 'Требуются параметры a и b'}), 400

        a = float(data['a'])
        b = float(data['b'])
        result = calculator.divide(a, b)

        return jsonify({'operation': 'divide', 'a': a, 'b': b, 'result': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/round', methods=['POST'])
def round_number():
    """API endpoint для округления чисел."""
    try:
        data = request.get_json()
        if not data or 'value' not in data or 'precision' not in data:
            return jsonify({'error': 'Требуются параметры value и precision'}), 400

        value = float(data['value'])
        precision = float(data['precision'])
        method = data.get('method', 'auto')

        # Валидация метода
        valid_methods = ['auto', 'up', 'down', 'banker', 'truncate']
        if method not in valid_methods:
            return jsonify({'error': f'Неподдерживаемый метод. Доступны: {", ".join(valid_methods)}'}), 400

        result = calculator.round_number(value, precision, method)

        return jsonify(
            {'operation': 'round', 'value': value, 'precision': precision, 'method': method, 'result': result}
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """
    API endpoint для получения истории вычислений.

    Возвращает сложную вложенную структуру JSON с метаданными.
    Эта структура создана специально для демонстрации генерации датаклассов
    на мастер-классе SQA Days 38.
    """
    try:
        start_time = datetime.now(timezone.utc)
        request_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        history = calculator.get_history()

        # Формируем сложную вложенную структуру
        history_items = []
        for idx, (operation, result) in enumerate(history):
            # Парсим операцию для получения типа и операндов
            op_type = 'unknown'
            operands = {'a': 0, 'b': 0}

            if '+' in operation:
                op_type = 'add'
                parts = operation.split('+')
                operands = {'a': float(parts[0].strip()), 'b': float(parts[1].strip())}
            elif '-' in operation:
                op_type = 'subtract'
                parts = operation.split('-')
                operands = {'a': float(parts[0].strip()), 'b': float(parts[1].strip())}
            elif '*' in operation:
                op_type = 'multiply'
                parts = operation.split('*')
                operands = {'a': float(parts[0].strip()), 'b': float(parts[1].strip())}
            elif '/' in operation:
                op_type = 'divide'
                parts = operation.split('/')
                operands = {'a': float(parts[0].strip()), 'b': float(parts[1].strip())}

            # Определяем точность для форматирования
            precision = 2 if isinstance(result, float) and not result.is_integer() else 0

            history_items.append(
                {
                    'id': idx + 1,
                    'operation': {'expression': operation, 'type': op_type, 'operands': operands},
                    'result': {
                        'value': result,
                        'formatted': f"{result:.{precision}f}" if precision > 0 else f"{int(result)}",
                        'precision': precision,
                    },
                    'metadata': {'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'), 'session_id': session_id},
                }
            )

        # Вычисляем время выполнения
        execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Формируем полный ответ с метаданными
        response = {
            'meta': {
                'user': {'id': 'calc-user-001', 'name': 'Calculator Service', 'role': 'system'},
                'timestamps': {
                    'created_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'timezone': 'UTC',
                    'request_id': request_id,
                },
                'status': {
                    'code': 'SUCCESS',
                    'message': 'История получена успешно',
                    'execution_time_ms': execution_time_ms,
                },
            },
            'data': {
                'history': history_items,
                'pagination': {
                    'total': len(history_items),
                    'page': 1,
                    'per_page': 50,
                    'has_more': len(history_items) >= 50,
                },
            },
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """API endpoint для очистки истории вычислений."""
    try:
        calculator.clear_history()
        return jsonify({'message': 'История очищена'})
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Универсальный API endpoint для всех операций."""
    try:
        data = request.get_json()
        operation = data['operation'].lower() if data and 'operation' in data else None

        # Для операции round нужны параметры value, precision и опционально method
        if operation == 'round':
            if not data or 'value' not in data or 'precision' not in data:
                return jsonify({'error': 'Требуются параметры operation, value и precision'}), 400
            value = float(data['value'])
            precision = float(data['precision'])
            method = data.get('method', 'auto')

            # Валидация метода
            valid_methods = ['auto', 'up', 'down', 'banker', 'truncate']
            if method not in valid_methods:
                return jsonify({'error': f'Неподдерживаемый метод. Доступны: {", ".join(valid_methods)}'}), 400

            result = calculator.round_number(value, precision, method)
            return jsonify(
                {'operation': operation, 'value': value, 'precision': precision, 'method': method, 'result': result}
            )

        # Для остальных операций нужны параметры a и b
        if not data or 'operation' not in data or 'a' not in data or 'b' not in data:
            return jsonify({'error': 'Требуются параметры operation, a и b'}), 400

        a = float(data['a'])
        b = float(data['b'])

        if operation == 'add':
            result = calculator.add(a, b)
        elif operation == 'subtract':
            result = calculator.subtract(a, b)
        elif operation == 'multiply':
            result = calculator.multiply(a, b)
        elif operation == 'divide':
            result = calculator.divide(a, b)
        else:
            return (
                jsonify({'error': 'Неподдерживаемая операция. Доступны: add, subtract, multiply, divide, round'}),
                400,
            )

        return jsonify({'operation': operation, 'a': a, 'b': b, 'result': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Обработчик для несуществующих endpoints."""
    return jsonify({'error': 'Endpoint не найден'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Обработчик для неподдерживаемых HTTP методов."""
    return jsonify({'error': 'Метод не поддерживается'}), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
