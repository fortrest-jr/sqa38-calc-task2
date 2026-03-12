"""
Marshmallow схемы для сериализации выходных данных (Response Schemas).
"""

from marshmallow import Schema, fields


class ErrorResponseSchema(Schema):
    """Схема для ответов с ошибками."""

    error = fields.Str(required=True)
    code = fields.Str(load_default=None)
    details = fields.Dict(load_default=None)


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


# Nested Schemas для сложных структур (History Response)


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
