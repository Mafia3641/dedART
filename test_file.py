#!/usr/bin/env python3
"""
Тестовый файл для демонстрации работы dedART Editor
"""

import sys
from pathlib import Path

def main():
    """Главная функция"""
    print("Добро пожаловать в dedART Editor!")
    print("Это тестовый файл для демонстрации возможностей редактора.")
    
    # Пример кода с различными элементами
    numbers = [1, 2, 3, 4, 5]
    sum_numbers = sum(numbers)
    
    # Строковые операции
    message = "Hello, World!"
    reversed_message = message[::-1]
    
    # Условные конструкции
    if sum_numbers > 10:
        print(f"Сумма чисел {numbers}: {sum_numbers}")
    else:
        print("Сумма меньше 10")
    
    # Циклы
    for i in range(5):
        print(f"Итерация {i + 1}")
    
    # Функции
    def calculate_factorial(n):
        """Вычисление факториала"""
        if n <= 1:
            return 1
        return n * calculate_factorial(n - 1)
    
    result = calculate_factorial(5)
    print(f"Факториал 5: {result}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 