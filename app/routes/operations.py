"""
Эндпоинты для математических операций калькулятора.
"""

from flask import Blueprint, jsonify, current_app
from app.validators import validate_request
from app.schemas import (
    BinaryOperationRequestSchema,
    RoundRequestSchema,
    CalculateRequestSchema,
    BinaryOperationResponseSchema,
    RoundResponseSchema,
    ErrorResponseSchema,
)

operations_bp = Blueprint('operations', __name__, url_prefix='/api')


@operations_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервиса."""
    return jsonify({'status': 'ok', 'message': 'Калькулятор работает'})


@operations_bp.route('/add', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def add(data):
    """Сложение двух чисел."""
    try:
        calculator = current_app.calculator
        result = calculator.add(data['a'], data['b'])
        response_data = {'operation': 'add', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@operations_bp.route('/subtract', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def subtract(data):
    """Вычитание двух чисел."""
    try:
        calculator = current_app.calculator
        result = calculator.subtract(data['a'], data['b'])
        response_data = {'operation': 'subtract', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@operations_bp.route('/multiply', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def multiply(data):
    """Умножение двух чисел."""
    try:
        calculator = current_app.calculator
        result = calculator.multiply(data['a'], data['b'])
        response_data = {'operation': 'multiply', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@operations_bp.route('/divide', methods=['POST'])
@validate_request(BinaryOperationRequestSchema)
def divide(data):
    """Деление двух чисел."""
    try:
        calculator = current_app.calculator
        result = calculator.divide(data['a'], data['b'])
        response_data = {'operation': 'divide', 'a': data['a'], 'b': data['b'], 'result': result}
        return jsonify(BinaryOperationResponseSchema().dump(response_data))
    except ValueError as e:
        error_response = ErrorResponseSchema().dump({'error': str(e), 'code': 'VALIDATION_ERROR'})
        return jsonify(error_response), 400
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500


@operations_bp.route('/round', methods=['POST'])
@validate_request(RoundRequestSchema)
def round_number(data):
    """Округление числа."""
    try:
        calculator = current_app.calculator
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


@operations_bp.route('/calculate', methods=['POST'])
@validate_request(CalculateRequestSchema)
def calculate(data):
    """Универсальный эндпоинт для всех операций."""
    try:
        calculator = current_app.calculator
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
