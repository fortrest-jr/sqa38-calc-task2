from flask import Flask, request, jsonify
from calculator import Calculator
from datetime import datetime, timezone
import uuid
from marshmallow import Schema, fields, validate, ValidationError, validates_schema
from functools import wraps

app = Flask(__name__)

# Создаем глобальный экземпляр калькулятора
calculator = Calculator()


# ============================================================================
# Schemas для валидации входных данных (Request Schemas)
# ============================================================================


class BinaryOperationRequestSchema(Schema):
    """Схема для операций с двумя операндами (сложение, вычитание, умножение, деление)."""

    a = fields.Float(
        required=True,
        error_messages={
            'required': 'Требуются параметры a и b',
            'invalid': 'Not a valid number.',
            'null': 'Требуются параметры a и b',
        },
    )
    b = fields.Float(
        required=True,
        error_messages={
            'required': 'Требуются параметры a и b',
            'invalid': 'Not a valid number.',
            'null': 'Требуются параметры a и b',
        },
    )


class RoundRequestSchema(Schema):
    """Схема для операции округления."""

    value = fields.Float(required=True, error_messages={'required': 'Требуются параметры value и precision'})
    precision = fields.Integer(required=True, error_messages={'required': 'Требуются параметры value и precision'})
    method = fields.Str(
        load_default='auto',
        validate=validate.OneOf(['auto', 'up', 'down', 'banker', 'truncate']),
        error_messages={'validator_failed': 'Неподдерживаемый метод. Доступны: auto, up, down, banker, truncate'},
    )


class CalculateRequestSchema(Schema):
    """Схема для универсального эндпоинта вычислений."""

    operation = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['add', 'subtract', 'multiply', 'divide', 'round'],
            error='Неподдерживаемая операция. Доступны: add, subtract, multiply, divide, round',
        ),
    )
    a = fields.Float(load_default=None)
    b = fields.Float(load_default=None)
    value = fields.Float(load_default=None)
    precision = fields.Integer(load_default=None)
    method = fields.Str(
        load_default='auto',
        validate=validate.OneOf(['auto', 'up', 'down', 'banker', 'truncate']),
        error_messages={'validator_failed': 'Неподдерживаемый метод. Доступны: auto, up, down, banker, truncate'},
    )

    @validates_schema
    def validate_operation_params(self, data, **kwargs):
        """Валидация параметров в зависимости от операции."""
        operation = data.get('operation')

        if operation == 'round':
            if data.get('value') is None or data.get('precision') is None:
                raise ValidationError('Для операции round требуются параметры value и precision')
        elif operation in ['add', 'subtract', 'multiply', 'divide']:
            if data.get('a') is None or data.get('b') is None:
                raise ValidationError(f'Для операции {operation} требуются параметры a и b')


class ErrorResponseSchema(Schema):
    """Схема для ответов с ошибками."""

    error = fields.Str(required=True)
    code = fields.Str(load_default=None)
    details = fields.Dict(load_default=None)


# ============================================================================
# Schemas для сериализации выходных данных (Response Schemas)
# ============================================================================


class BinaryOperationResponseSchema(Schema):
    """Схема для ответа операций с двумя операндами."""

    operation = fields.Str(required=True)
    a = fields.Float(required=True)
    b = fields.Float(required=True)
    result = fields.Float(required=True)


class RoundResponseSchema(Schema):
    """Схема для ответа операции округления."""

    operation = fields.Str(required=True)
    value = fields.Float(required=True)
    precision = fields.Integer(required=True)
    method = fields.Str(required=True)
    result = fields.Float(required=True)


# ============================================================================
# Nested Schemas для сложных структур (History Response)
# ============================================================================


class OperandsSchema(Schema):
    """Схема для операндов операции."""

    a = fields.Float(required=True)
    b = fields.Float(required=True)


class OperationDetailSchema(Schema):
    """Схема для детальной информации об операции."""

    expression = fields.Str(required=True)
    type = fields.Str(required=True)
    operands = fields.Nested(OperandsSchema, required=True)


class ResultDetailSchema(Schema):
    """Схема для детальной информации о результате."""

    value = fields.Float(required=True)
    formatted = fields.Str(required=True)
    precision = fields.Integer(required=True)


class ItemMetadataSchema(Schema):
    """Схема для метаданных элемента истории."""

    timestamp = fields.Str(required=True)
    session_id = fields.Str(required=True)


class HistoryItemSchema(Schema):
    """Схема для элемента истории вычислений."""

    id = fields.Integer(required=True)
    operation = fields.Nested(OperationDetailSchema, required=True)
    result = fields.Nested(ResultDetailSchema, required=True)
    metadata = fields.Nested(ItemMetadataSchema, required=True)


class PaginationSchema(Schema):
    """Схема для пагинации."""

    total = fields.Integer(required=True)
    page = fields.Integer(required=True)
    per_page = fields.Integer(required=True)
    has_more = fields.Boolean(required=True)


class UserSchema(Schema):
    """Схема для информации о пользователе."""

    id = fields.Str(required=True)
    name = fields.Str(required=True)
    role = fields.Str(required=True)


class TimestampsSchema(Schema):
    """Схема для временных меток."""

    created_at = fields.Str(required=True)
    timezone = fields.Str(required=True)
    request_id = fields.Str(required=True)


class StatusSchema(Schema):
    """Схема для статуса операции."""

    code = fields.Str(required=True)
    message = fields.Str(required=True)
    execution_time_ms = fields.Integer(required=True)


class MetaSchema(Schema):
    """Схема для метаданных ответа."""

    user = fields.Nested(UserSchema, required=True)
    timestamps = fields.Nested(TimestampsSchema, required=True)
    status = fields.Nested(StatusSchema, required=True)


class HistoryDataSchema(Schema):
    """Схема для данных истории."""

    history = fields.List(fields.Nested(HistoryItemSchema), required=True)
    pagination = fields.Nested(PaginationSchema, required=True)


class HistoryResponseSchema(Schema):
    """Схема для полного ответа с историей вычислений."""

    meta = fields.Nested(MetaSchema, required=True)
    data = fields.Nested(HistoryDataSchema, required=True)


# ============================================================================
# Декоратор для валидации входных данных
# ============================================================================


def format_validation_errors(messages):
    """
    Форматирует ошибки валидации Marshmallow в читаемую строку.

    Args:
        messages: Словарь с ошибками валидации от Marshmallow

    Returns:
        Отформатированная строка с ошибками
    """
    errors = []
    for field, field_errors in messages.items():
        if isinstance(field_errors, list):
            for error in field_errors:
                # Проверяем типичные ошибки Marshmallow и заменяем на более понятные
                if 'Not a valid' in str(error):
                    errors.append('Некорректные данные: could not convert string to float')
                else:
                    errors.append(str(error))
        elif isinstance(field_errors, dict):
            # Рекурсивная обработка вложенных ошибок
            errors.append(f"{field}: {format_validation_errors(field_errors)}")
        else:
            errors.append(str(field_errors))
    return '; '.join(errors) if errors else 'Ошибка валидации данных'


def validate_request(schema_class):
    """
    Декоратор для валидации входных данных с помощью Marshmallow схемы.

    Args:
        schema_class: Класс Marshmallow схемы для валидации

    Returns:
        Обертка, которая валидирует данные перед выполнением функции
    """

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            schema = schema_class()
            try:
                # Получаем JSON данные (silent=False чтобы выбросить исключение при некорректном JSON)
                json_data = request.get_json(force=True, silent=False)

                # Валидируем входные данные
                data = schema.load(json_data)
            except ValidationError as err:
                # Используем структурированную обработку ошибок
                error_text = format_validation_errors(err.messages)
                error_response = ErrorResponseSchema().dump(
                    {'error': error_text, 'code': 'VALIDATION_ERROR', 'details': err.messages}
                )
                return jsonify(error_response), 400
            except Exception as e:
                # Возвращаем 500 для ошибок парсинга JSON и других внутренних ошибок
                error_response = ErrorResponseSchema().dump(
                    {'error': f'Некорректные данные: {str(e)}', 'code': 'PARSE_ERROR'}
                )
                return jsonify(error_response), 500

            # Передаем валидированные данные в функцию
            return f(data, *args, **kwargs)

        return wrapper

    return decorator


# ============================================================================
# Эндпоинты API
# ============================================================================


@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервиса."""
    return jsonify({'status': 'ok', 'message': 'Калькулятор работает'})


@app.route('/api/add', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def add(data):
    """Сложение двух чисел."""
    try:
        result = calculator.add(data['a'], data['b'])
        response_data = {'operation': 'add', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/subtract', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def subtract(data):
    """Вычитание двух чисел."""
    try:
        result = calculator.subtract(data['a'], data['b'])
        response_data = {'operation': 'subtract', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/multiply', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def multiply(data):
    """Умножение двух чисел."""
    try:
        result = calculator.multiply(data['a'], data['b'])
        response_data = {'operation': 'multiply', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/divide', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def divide(data):
    """Деление двух чисел."""
    try:
        result = calculator.divide(data['a'], data['b'])
        response_data = {'operation': 'divide', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except ValueError as e:
        error_response = ErrorResponseSchema().dump({'error': str(e), 'code': 'VALIDATION_ERROR'})
        return jsonify(error_response), 400
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/round', methods=['POST'])
@validate_request(RoundRequestSchema)
def round_number(data):
    """Округление числа."""
    try:
        result = calculator.round_number(data['value'], data['precision'], data['method'])
        response_data = {
            'operation': 'round',
            'value': data['value'],
            'precision': data['precision'],
            'method': data['method'],
            'result': result,
        }
        return jsonify(RoundResponseSchema().dump(response_data))
    except ValueError as e:
        error_response = ErrorResponseSchema().dump({'error': str(e), 'code': 'VALIDATION_ERROR'})
        return jsonify(error_response), 400
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Получение истории вычислений."""
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

        # Используем схему для валидации и сериализации ответа
        return jsonify(HistoryResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    """Очистка истории вычислений."""
    try:
        calculator.clear_history()
        return jsonify({'message': 'История очищена'})
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@app.route('/api/calculate', methods=['POST'])
@validate_request(CalculateRequestSchema)
def calculate(data):
    """Универсальный эндпоинт для всех операций."""
    try:
        operation = data['operation'].lower()

        # Для операции round
        if operation == 'round':
            result = calculator.round_number(data['value'], data['precision'], data.get('method', 'auto'))
            response_data = {
                'operation': operation,
                'value': data['value'],
                'precision': data['precision'],
                'method': data.get('method', 'auto'),
                'result': result,
            }
            return jsonify(RoundResponseSchema().dump(response_data))

        # Для остальных операций
        a = data['a']
        b = data['b']

        if operation == 'add':
            result = calculator.add(a, b)
        elif operation == 'subtract':
            result = calculator.subtract(a, b)
        elif operation == 'multiply':
            result = calculator.multiply(a, b)
        elif operation == 'divide':
            result = calculator.divide(a, b)
        else:
            error_response = ErrorResponseSchema().dump(
                {'error': 'Неподдерживаемая операция', 'code': 'INVALID_OPERATION'}
            )
            return jsonify(error_response), 400

        response_data = {'operation': operation, 'a': a, 'b': b, 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except ValueError as e:
        error_response = ErrorResponseSchema().dump({'error': str(e), 'code': 'VALIDATION_ERROR'})
        return jsonify(error_response), 400
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


# ============================================================================
# Обработчики ошибок
# ============================================================================


@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки."""
    return jsonify({'error': 'Endpoint не найден'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Обработка 405 ошибки."""
    return jsonify({'error': 'Метод не поддерживается'}), 405


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
