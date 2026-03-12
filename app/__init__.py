"""
Flask application factory для калькулятора.
"""

from flask import Flask
from calculator import Calculator


def create_app():
    """Создание и настройка Flask приложения."""
    app = Flask(__name__)

    # Создаём глобальный экземпляр калькулятора
    # В продакшене лучше использовать app.config или dependency injection
    app.calculator = Calculator()

    # Регистрируем blueprints
    from app.routes.operations import operations_bp
    from app.routes.history import history_bp

    app.register_blueprint(operations_bp)
    app.register_blueprint(history_bp)

    # Регистрируем обработчики ошибок
    from app.errors import register_error_handlers

    register_error_handlers(app)

    return app


# Создаём экземпляр приложения для обратной совместимости
app = create_app()
calculator = app.calculator
