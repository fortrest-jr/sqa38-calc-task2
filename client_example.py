"""
Пример клиента для демонстрации работы с API калькулятора.
"""

import requests


class CalculatorClient:
    """Клиент для работы с API калькулятора."""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def health_check(self):
        """Проверка работоспособности API."""
        response = requests.get(f"{self.base_url}/api/health")
        return response.json()

    def add(self, a, b):
        """Сложение."""
        data = {"a": a, "b": b}
        response = requests.post(f"{self.base_url}/api/add", json=data)
        return response.json()

    def subtract(self, a, b):
        """Вычитание."""
        data = {"a": a, "b": b}
        response = requests.post(f"{self.base_url}/api/subtract", json=data)
        return response.json()

    def multiply(self, a, b):
        """Умножение."""
        data = {"a": a, "b": b}
        response = requests.post(f"{self.base_url}/api/multiply", json=data)
        return response.json()

    def divide(self, a, b):
        """Деление."""
        data = {"a": a, "b": b}
        response = requests.post(f"{self.base_url}/api/divide", json=data)
        return response.json()

    def round_number(self, value, precision, method="auto"):
        """Округление числа."""
        data = {"value": value, "precision": precision, "method": method}
        response = requests.post(f"{self.base_url}/api/round", json=data)
        return response.json()

    def calculate(self, operation, a, b):
        """Универсальный метод для вычислений."""
        data = {"operation": operation, "a": a, "b": b}
        response = requests.post(f"{self.base_url}/api/calculate", json=data)
        return response.json()

    def get_history(self):
        """Получить историю вычислений."""
        response = requests.get(f"{self.base_url}/api/history")
        return response.json()

    def clear_history(self):
        """Очистить историю вычислений."""
        response = requests.delete(f"{self.base_url}/api/history")
        return response.json()


def demo():
    """Демонстрация работы с API."""
    client = CalculatorClient()

    print("=== ДЕМОНСТРАЦИЯ API КАЛЬКУЛЯТОРА ===\n")

    # Проверка работоспособности
    print("1. Проверка работоспособности API:")
    health = client.health_check()
    print(f"   Статус: {health['status']}")
    print(f"   Сообщение: {health['message']}\n")

    # Выполнение операций
    print("2. Выполнение математических операций:")

    # Сложение
    result = client.add(10, 5)
    print(f"   10 + 5 = {result['result']}")

    # Вычитание
    result = client.subtract(10, 3)
    print(f"   10 - 3 = {result['result']}")

    # Умножение
    result = client.multiply(4, 6)
    print(f"   4 * 6 = {result['result']}")

    # Деление
    result = client.divide(15, 3)
    print(f"   15 / 3 = {result['result']}")

    # Округление чисел (неоднозначная логика!)
    print("\n   === НЕОДНОЗНАЧНАЯ ЛОГИКА ОКРУГЛЕНИЯ ===")
    result = client.round_number(3.14159, 2, "auto")
    print(f"   round(3.14159, 2, auto) = {result['result']}")

    result = client.round_number(3.14159, 2, "up")
    print(f"   round(3.14159, 2, up) = {result['result']}")

    result = client.round_number(3.14159, 2, "down")
    print(f"   round(3.14159, 2, down) = {result['result']}")

    result = client.round_number(1234, -2, "auto")
    print(f"   round(1234, -2, auto) = {result['result']} (округление до разрядов)")

    result = client.round_number(0, 2, "auto")
    print(f"   round(0, 2, auto) = {result['result']} (особый случай)")

    # Универсальный endpoint
    result = client.calculate("add", 2, 8)
    print(f"   Универсальный: 2 + 8 = {result['result']}")

    result = client.calculate("round", 3.14, 1)
    print(f"   Универсальный: round(3.14, 1) = {result['result']}\n")

    # Просмотр истории
    print("3. История вычислений:")
    history = client.get_history()
    print(f"   Количество операций: {history['data']['pagination']['total']}")
    for i, item in enumerate(history['data']['history'], 1):
        print(f"   {i}. {item['operation']['expression']} = {item['result']['value']}")

    print("\n=== ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА ===")


if __name__ == "__main__":
    try:
        demo()
    except requests.exceptions.ConnectionError:
        print("Ошибка: не удается подключиться к API.")
        print("Убедитесь, что сервер запущен: python app.py")
    except Exception as e:
        print(f"Ошибка: {e}")
