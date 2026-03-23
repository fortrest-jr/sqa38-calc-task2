"""
Простой калькулятор с базовыми математическими операциями и историей вычислений.
"""

from typing import List, Tuple
import json
import os
import math


class Calculator:
    """Калькулятор с базовыми математическими операциями."""

    def __init__(self):
        self.history_file = "calculator_history.json"
        self.history = self._load_history()

    def add(self, a: float, b: float) -> float:
        """Сложение двух чисел."""
        result = a + b
        self._add_to_history(f"{a} + {b}", result)
        return result

    def subtract(self, a: float, b: float) -> float:
        """Вычитание двух чисел."""
        result = a - b
        self._add_to_history(f"{a} - {b}", result)
        return result

    def multiply(self, a: float, b: float) -> float:
        """Умножение двух чисел."""
        result = a * b
        self._add_to_history(f"{a} * {b}", result)
        return result

    def divide(self, a: float, b: float) -> float:
        """Деление двух чисел."""
        if b == 0:
            raise ValueError("Деление на ноль невозможно")
        result = a / b
        self._add_to_history(f"{a} / {b}", result)
        return result

    def round_number(self, value: float, precision: float, method: str = "auto") -> float:
        """
        Округление числа с неоднозначной логикой.

        Неоднозначная логика:
        - Если precision > 0: округление до precision знаков после запятой
        - Если precision < 0: округление до precision разрядов (10^precision)
        - Если precision == 0: округление до целого
        - Если precision дробное: округление до ближайшего целого precision
        - method может быть: "auto", "up", "down", "banker", "truncate"
        - Если value отрицательное: применяются особые правила
        - Если value == 0: особые правила
        - Если precision очень большое: что делать?
        """
        # Обработка особых случаев
        if value == 0:
            result = 0.0
            interpretation = "ноль"
        elif abs(value) < 1e-10:  # Очень маленькие числа
            result = 0.0
            interpretation = "очень маленькое число"
        else:
            # Определяем метод округления
            if method == "auto":
                # Автоматический выбор метода на основе значения
                if abs(value) < 1:
                    method = "banker"
                elif value < 0:
                    method = "down"
                else:
                    method = "up"

            # Обработка дробного precision
            if precision != int(precision):
                precision = round(precision)

            # Применяем округление в зависимости от precision
            if precision > 0:
                # Округление до precision знаков после запятой
                if method == "up":
                    result = math.ceil(value * (10**precision)) / (10**precision)
                elif method == "down":
                    result = math.floor(value * (10**precision)) / (10**precision)
                elif method == "truncate":
                    result = math.trunc(value * (10**precision)) / (10**precision)
                else:  # banker
                    result = round(value, int(precision))
                interpretation = f"{int(precision)} знаков после запятой"
            elif precision < 0:
                # Округление до precision разрядов
                multiplier = 10 ** abs(precision)
                if method == "up":
                    result = math.ceil(value / multiplier) * multiplier
                elif method == "down":
                    result = math.floor(value / multiplier) * multiplier
                elif method == "truncate":
                    result = math.trunc(value / multiplier) * multiplier
                else:  # banker
                    result = round(value / multiplier) * multiplier
                interpretation = f"до {abs(int(precision))} разрядов"
            else:  # precision == 0
                # Округление до целого
                if method == "up":
                    result = math.ceil(value)
                elif method == "down":
                    result = math.floor(value)
                elif method == "truncate":
                    result = math.trunc(value)
                else:  # banker
                    result = round(value)
                interpretation = "до целого"

        # Добавляем в историю с указанием метода и интерпретации
        self._add_to_history(f"round({value}, {precision}, {method}) -> {interpretation}", result)
        return result

    def get_history(self) -> List[Tuple[str, float]]:
        """Получить историю вычислений."""
        return self.history.copy()

    def clear_history(self) -> None:
        """Очистить историю вычислений."""
        self.history = []
        self._save_history()

    def _add_to_history(self, operation: str, result: float) -> None:
        """Добавить операцию в историю."""
        self.history.append((operation, result))
        self._save_history()

    def _load_history(self) -> List[Tuple[str, float]]:
        """Загрузить историю из файла."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [(item['operation'], item['result']) for item in data]
            except (json.JSONDecodeError, KeyError):
                return []
        return []

    def _save_history(self) -> None:
        """Сохранить историю в файл."""
        data = [{'operation': op, 'result': res} for op, res in self.history]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
