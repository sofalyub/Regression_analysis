#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для установки необходимых пакетов для приложения анализа регрессии
"""

import sys
import subprocess
import os

def main():
    """
    Основная функция для установки зависимостей
    """
    print("Установка необходимых пакетов для приложения анализа регрессии...")
    
    # Проверяем наличие pip
    try:
        import pip
    except ImportError:
        print("Ошибка: pip не установлен. Пожалуйста, установите pip перед запуском этого скрипта.")
        sys.exit(1)
    
    # Определяем путь к файлу requirements.txt
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    
    if not os.path.exists(requirements_path):
        print(f"Ошибка: Файл requirements.txt не найден по пути: {requirements_path}")
        sys.exit(1)
    
    print(f"Найден файл requirements.txt по пути: {requirements_path}")
    
    # Устанавливаем пакеты из requirements.txt
    try:
        print("Установка зависимостей...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])
        print("Зависимости успешно установлены!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при установке зависимостей: {e}")
        sys.exit(1)
    
    print("\nУстановка завершена. Теперь вы можете запустить приложение с помощью python main.py")

if __name__ == "__main__":
    main()