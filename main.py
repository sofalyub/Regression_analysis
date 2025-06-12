#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Главный файл приложения для анализа регрессий

Это приложение позволяет загружать данные из файлов Excel,
выбирать переменные для регрессионного анализа и просматривать результаты
в виде статистик, интерпретаций и графиков.
"""

import sys
import os
import traceback

# Добавляем директорию проекта в путь
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)

# Устанавливаем обработчик исключений для вывода ошибок в консоль
def exception_hook(exctype, value, tb):
    """
    Функция для вывода исключений в консоль
    """
    print(''.join(traceback.format_exception(exctype, value, tb)))
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

from ui.app import run_app


def main():
    """
    Основная функция для запуска приложения
    """
    # Проверяем наличие директории data
    data_dir = os.path.join(project_path, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Создана директория для данных: {data_dir}")
    
    # Создаем директорию для иконок, если она не существует
    icons_dir = os.path.join(project_path, 'ui', 'icons')
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
        print(f"Создана директория для иконок: {icons_dir}")
    
    print("Запуск приложения для анализа регрессии...")
    run_app()


if __name__ == "__main__":
    main()