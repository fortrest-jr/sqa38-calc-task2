"""
Эндпоинты для работы с историей вычислений.
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone
import uuid
from app.schemas.response import HistoryResponseSchema, ErrorResponseSchema

history_bp = Blueprint('history', __name__, url_prefix='/api')


@history_bp.route('/history', methods=['GET'])
def get_history():
    """Получение истории вычислений."""
    try:
        calculator = current_app.calculator
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

            if operation.startswith('round('):
                op_type = 'round'
                operands = {'a': 0, 'b': 0}
            elif ' + ' in operation:
                op_type = 'add'
                parts = operation.split(' + ')
                operands = {'a': float(parts[0]), 'b': float(parts[1])}
            elif ' - ' in operation:

                op_type = 'subtract'
                parts = operation.split(' - ')
                operands = {'a': float(parts[0]), 'b': float(parts[1])}
            elif ' * ' in operation:
                op_type = 'multiply'
                parts = operation.split(' * ')
                operands = {'a': float(parts[0]), 'b': float(parts[1])}
            elif ' / ' in operation:
                op_type = 'divide'
                parts = operation.split(' / ')
                operands = {'a': float(parts[0]), 'b': float(parts[1])}

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


@history_bp.route('/history', methods=['DELETE'])
def clear_history():
    """Очистка истории вычислений."""
    try:
        calculator = current_app.calculator
        calculator.clear_history()
        return jsonify({'message': 'История очищена'})
    except Exception as e:
        error_response = ErrorResponseSchema().dump({'error': f'Внутренняя ошибка: {str(e)}', 'code': 'INTERNAL_ERROR'})
        return jsonify(error_response), 500
