"""
Flask application factory для калькулятора.
"""

from flask import Flask, g
from calculator import Calculator


def get_calculator():
    """
    Получить экземпляр калькулятора для текущего запроса.
    Использует Flask g для изоляции состояния между запросами.
    """
    if 'calculator' not in g:
        g.calculator = Calculator()
    return g.calculator


def create_app(config=None):
    """
    Создание и настройка Flask приложения.

    Args:
        config: Опциональный словарь с конфигурацией приложения
    """
    app = Flask(__name__)

    # Применяем конфигурацию если передана
    if config:
        app.config.update(config)

    # Сохраняем функцию получения калькулятора в app.extensions
    # Это позволяет тестам и другим компонентам использовать свой калькулятор
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    app.extensions['get_calculator'] = get_calculator

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

# Для обратной совместимости с тестами создаём глобальный калькулятор
# В продакшене лучше использовать get_calculator() через app context
calculator = Calculator()
app.calculator = calculator
