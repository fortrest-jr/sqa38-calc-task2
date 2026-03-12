"""
Декораторы для валидации входных данных.
"""

from functools import wraps
from flask import request, jsonify
from marshmallow import ValidationError
from app.schemas.response import ErrorResponseSchema


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
