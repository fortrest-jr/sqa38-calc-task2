"""
Точка входа Flask приложения калькулятора.
Для обратной совместимости с существующими тестами и запуском.
"""

from app import app, calculator

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
