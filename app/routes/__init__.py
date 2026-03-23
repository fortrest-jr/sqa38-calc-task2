"""
Flask blueprints для роутов калькулятора.
"""

from app.routes.operations import operations_bp
from app.routes.history import history_bp

__all__ = ['operations_bp', 'history_bp']
