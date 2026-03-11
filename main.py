"""
CLI интерфейс для калькулятора.
"""

from calculator import Calculator


def print_menu():
    """Вывести меню калькулятора."""
    print("\n=== КАЛЬКУЛЯТОР ===")
    print("1. Сложение")
    print("2. Вычитание")
    print("3. Умножение")
    print("4. Деление")
    print("5. Показать историю")
    print("6. Очистить историю")
    print("0. Выход")
    print("==================")


def get_number(prompt: str) -> float:
    """Получить число от пользователя."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Ошибка: введите корректное число")


def show_history(calc: Calculator):
    """Показать историю вычислений."""
    history = calc.get_history()
    if not history:
        print("История пуста")
        return

    print("\n=== ИСТОРИЯ ВЫЧИСЛЕНИЙ ===")
    for i, (operation, result) in enumerate(history, 1):
        print(f"{i}. {operation} = {result}")
    print("=========================")


def main():
    """Основная функция программы."""
    calc = Calculator()

    print("Добро пожаловать в калькулятор!")

    while True:
        print_menu()
        choice = input("Выберите операцию (0-6): ").strip()

        if choice == "0":
            print("До свидания!")
            break
        elif choice == "1":
            a = get_number("Введите первое число: ")
            b = get_number("Введите второе число: ")
            result = calc.add(a, b)
            print(f"Результат: {a} + {b} = {result}")
        elif choice == "2":
            a = get_number("Введите первое число: ")
            b = get_number("Введите второе число: ")
            result = calc.subtract(a, b)
            print(f"Результат: {a} - {b} = {result}")
        elif choice == "3":
            a = get_number("Введите первое число: ")
            b = get_number("Введите второе число: ")
            result = calc.multiply(a, b)
            print(f"Результат: {a} * {b} = {result}")
        elif choice == "4":
            a = get_number("Введите первое число: ")
            b = get_number("Введите второе число: ")
            try:
                result = calc.divide(a, b)
                print(f"Результат: {a} / {b} = {result}")
            except ValueError as e:
                print(f"Ошибка: {e}")
        elif choice == "5":
            show_history(calc)
        elif choice == "6":
            calc.clear_history()
            print("История очищена")
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
