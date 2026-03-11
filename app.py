from flask import Flask, request, jsonify
from calculator import Calculator
from datetime import datetime, timezone
import uuid
from marshmallow import Schema, fields

app = Flask(__name__)

# Создаем глобальный экземпляр калькулятора
calculator = Calculator()


# Marshmallow Schema для API ответов (используется для документации и валидации)
# Эти схемы определяют структуру данных, но не используются напрямую для создания объектов
class UserSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    role = fields.Str(required=True)


class TimestampsSchema(Schema):
    created_at = fields.Str(required=True)
    timezone = fields.Str(required=True)
    request_id = fields.Str(required=True)


class StatusSchema(Schema):
    code = fields.Str(required=True)
    message = fields.Str(required=True)
    execution_time_ms = fields.Int(required=True)


class MetaSchema(Schema):
    user = fields.Nested(UserSchema, required=True)
    timestamps = fields.Nested(TimestampsSchema, required=True)
    status = fields.Nested(StatusSchema, required=True)


class OperandsSchema(Schema):
    a = fields.Float(required=True)
    b = fields.Float(required=True)


class OperationSchema(Schema):
    expression = fields.Str(required=True)
    type = fields.Str(required=True)
    operands = fields.Nested(OperandsSchema, required=True)


class ResultSchema(Schema):
    value = fields.Float(required=True)
    formatted = fields.Str(required=True)
    precision = fields.Int(required=True)


class ItemMetadataSchema(Schema):
    timestamp = fields.Str(required=True)
    session_id = fields.Str(required=True)


class HistoryItemSchema(Schema):
    id = fields.Int(required=True)
    operation = fields.Nested(OperationSchema, required=True)
    result = fields.Nested(ResultSchema, required=True)
    metadata = fields.Nested(ItemMetadataSchema, required=True)


class PaginationSchema(Schema):
    total = fields.Int(required=True)
    page = fields.Int(required=True)
    per_page = fields.Int(required=True)
    has_more = fields.Bool(required=True)


class DataSchema(Schema):
    history = fields.List(fields.Nested(HistoryItemSchema), required=True)
    pagination = fields.Nested(PaginationSchema, required=True)


class HistoryResponseSchema(Schema):
    meta = fields.Nested(MetaSchema, required=True)
    data = fields.Nested(DataSchema, required=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Калькулятор работает'})


@app.route('/api/add', methods=['POST'])
def add():
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
    try:
        start_time = datetime.now(timezone.utc)
        request_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        history = calculator.get_history()

        # Формируем сложную вложенную структуру согласно HistoryResponseSchema
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
                    'metadata': {
                        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                        'session_id': session_id,
                    },
                }
            )

        # Вычисляем время выполнения
        execution_time_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        # Формируем полный ответ с метаданными согласно HistoryResponseSchema
        response_data = {
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

        # Валидация структуры через Marshmallow Schema
        schema = HistoryResponseSchema()
        validated_data = schema.dump(schema.load(response_data))

        return jsonify(validated_data)
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    try:
        calculator.clear_history()
        return jsonify({'message': 'История очищена'})
    except Exception as e:
        return jsonify({'error': f'Внутренняя ошибка: {str(e)}'}), 500


@app.route('/api/calculate', methods=['POST'])
def calculate():
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
    return jsonify({'error': 'Endpoint не найден'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Метод не поддерживается'}), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
