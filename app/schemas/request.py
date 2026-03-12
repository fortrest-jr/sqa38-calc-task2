"""
Marshmallow схемы для валидации входных данных (Request Schemas).
"""

from marshmallow import Schema, fields, validate, ValidationError, validates_schema


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
