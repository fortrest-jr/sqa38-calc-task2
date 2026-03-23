"""
Обработчики ошибок Flask приложения.
"""

from flask import jsonify


def register_error_handlers(app):
    """
    Регистрация обработчиков ошибок для Flask приложения.

    Args:
        app: Flask приложение
    """

    @app.errorhandler(404)
    def not_found(error):
        """Обработка 404 ошибки."""
        return jsonify({'error': 'Endpoint не найден'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Обработка 405 ошибки."""
        return jsonify({'error': 'Метод не поддерживается'}), 405
