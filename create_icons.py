#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для создания простых иконок для приложения
"""

import os
import sys
import numpy as np
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QIcon, QPixmap, QPainterPath
from PyQt5.QtWidgets import QApplication

# Путь к директории с иконками
ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ui', 'icons')

# Цвета
COLORS = {
    'primary': '#1976D2',  # Основной цвет (синий)
    'primary_light': '#42A5F5',  # Светлый основной
    'primary_dark': '#0D47A1',  # Темный основной
    'secondary': '#26A69A',  # Дополнительный цвет (бирюзовый)
    'secondary_light': '#4DB6AC',  # Светлый дополнительный
    'secondary_dark': '#00796B',  # Темный дополнительный
    'accent': '#FFC107',  # Акцентный цвет (янтарный)
    'white': '#FFFFFF',
    'gray': '#9E9E9E',
    'error': '#D32F2F'
}


def create_icon(name, draw_func, size=64):
    """
    Создает иконку и сохраняет её в директории иконок
    
    Args:
        name (str): Имя иконки
        draw_func (callable): Функция для рисования иконки
        size (int): Размер иконки в пикселях
    """
    # Создаем QPixmap
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    # Создаем QPainter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    
    # Рисуем иконку
    draw_func(painter, size)
    
    # Завершаем рисование
    painter.end()
    
    # Сохраняем иконку
    file_path = os.path.join(ICONS_DIR, f"{name}.png")
    pixmap.save(file_path)
    print(f"Иконка сохранена: {file_path}")
    
    return pixmap


def draw_file_icon(painter, size):
    """Рисует иконку файла"""
    # Размеры и отступы - преобразуем в целые числа
    margin = int(size * 0.1)
    width = int(size - 2 * margin)
    height = int(size - 2 * margin)
    corner = int(size * 0.15)
    
    # Рисуем документ с загнутым уголком
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor('#FFFFFF')))
    painter.drawRoundedRect(margin, margin, width, height, 5, 5)
    
    # Рисуем границу документа
    painter.setPen(QPen(QColor(COLORS['primary']), 2))
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(margin, margin, width, height, 5, 5)
    
    # Рисуем загнутый уголок
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor(COLORS['primary_light'])))
    painter.drawRect(size - margin - corner, margin, corner, corner)
    
    # Рисуем линию загиба
    painter.setPen(QPen(QColor(COLORS['primary']), 2))
    painter.drawLine(size - margin - corner, margin, size - margin - corner, margin + corner)
    painter.drawLine(size - margin - corner, margin + corner, size - margin, margin + corner)
    
    # Рисуем линии текста
    line_margin = int(size * 0.25)
    line_height = int(size * 0.08)
    line_spacing = int(size * 0.14)
    
    painter.setPen(QPen(QColor(COLORS['gray']), 1))
    for i in range(4):
        y = margin + line_margin + i * line_spacing
        painter.drawLine(margin + line_margin, y, size - margin - line_margin, y)


def draw_chart_icon(painter, size):
    """Рисует иконку графика"""
    # Размеры и отступы - преобразуем в целые числа
    margin = int(size * 0.15)
    width = int(size - 2 * margin)
    height = int(size - 2 * margin)
    
    # Рисуем фон
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor('#FFFFFF')))
    painter.drawRect(margin, margin, width, height)
    
    # Рисуем оси
    painter.setPen(QPen(QColor('#000000'), 2))
    painter.drawLine(margin, size - margin, size - margin, size - margin)  # Ось X
    painter.drawLine(margin, margin, margin, size - margin)  # Ось Y
    
    # Рисуем линию графика - преобразуем все координаты в целые числа
    points = [
        (int(margin + width * 0.1), int(margin + height * 0.7)),
        (int(margin + width * 0.3), int(margin + height * 0.4)),
        (int(margin + width * 0.5), int(margin + height * 0.6)),
        (int(margin + width * 0.7), int(margin + height * 0.2)),
        (int(margin + width * 0.9), int(margin + height * 0.3))
    ]
    
    # Рисуем линию
    painter.setPen(QPen(QColor(COLORS['primary']), 3))
    for i in range(len(points) - 1):
        painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
    
    # Рисуем точки
    painter.setPen(QPen(QColor(COLORS['primary']), 1))
    painter.setBrush(QBrush(QColor('#FFFFFF')))
    for point in points:
        painter.drawEllipse(point[0] - 4, point[1] - 4, 8, 8)


def draw_data_icon(painter, size):
    """Рисует иконку данных"""
    # Размеры и отступы - преобразуем в целые числа
    margin = int(size * 0.15)
    width = int(size - 2 * margin)
    height = int(size - 2 * margin)
    
    # Рисуем фон таблицы
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor('#FFFFFF')))
    painter.drawRect(margin, margin, width, height)
    
    # Рисуем рамку таблицы
    painter.setPen(QPen(QColor(COLORS['primary']), 2))
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(margin, margin, width, height)
    
    # Рисуем заголовок таблицы
    header_height = int(height * 0.2)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor(COLORS['primary_light'])))
    painter.drawRect(margin, margin, width, header_height)
    
    # Рисуем линии таблицы
    painter.setPen(QPen(QColor(COLORS['gray']), 1))
    
    # Горизонтальные линии
    row_count = 4
    row_height = (height - header_height) / row_count
    for i in range(1, row_count + 1):
        y = int(margin + header_height + i * row_height)
        painter.drawLine(margin, y, margin + width, y)
    
    # Вертикальные линии
    col_count = 3
    col_width = width / col_count
    for i in range(1, col_count):
        x = int(margin + i * col_width)
        painter.drawLine(x, margin, x, margin + height)


def draw_settings_icon(painter, size):
    """Рисует иконку настроек"""
    # Размеры и отступы - преобразуем в целые числа
    margin = int(size * 0.15)
    center = int(size / 2)
    radius = int(size * 0.3)
    tooth_length = int(size * 0.12)
    
    # Рисуем внешний круг
    painter.setPen(QPen(QColor(COLORS['gray']), 2))
    painter.setBrush(QBrush(QColor('#FFFFFF')))
    painter.drawEllipse(center - radius, center - radius, radius * 2, radius * 2)
    
    # Рисуем зубцы шестеренки
    tooth_count = 8
    angle_step = 360 / tooth_count
    for i in range(tooth_count):
        angle = i * angle_step
        rad_angle = angle * 3.14159 / 180
        
        x1 = int(center + radius * 0.8 * (1 if i % 2 == 0 else 0.9) * np.cos(rad_angle))
        y1 = int(center + radius * 0.8 * (1 if i % 2 == 0 else 0.9) * np.sin(rad_angle))
        
        x2 = int(center + (radius + tooth_length) * np.cos(rad_angle))
        y2 = int(center + (radius + tooth_length) * np.sin(rad_angle))
        
        painter.drawLine(x1, y1, x2, y2)
    
    # Рисуем внутренний круг
    inner_radius = int(radius * 0.5)
    painter.setPen(QPen(QColor(COLORS['primary']), 2))
    painter.setBrush(QBrush(QColor(COLORS['primary_light'])))
    painter.drawEllipse(center - inner_radius, center - inner_radius, inner_radius * 2, inner_radius * 2)


def draw_down_arrow_icon(painter, size):
    """Рисует иконку стрелки вниз"""
    # Размеры и отступы - преобразуем в целые числа
    margin = int(size * 0.2)
    width = int(size - 2 * margin)
    height = int(width * 0.6)
    
    # Рисуем треугольник
    painter.setPen(Qt.NoPen)
    painter.setBrush(QBrush(QColor(COLORS['primary'])))
    
    points = [
        (margin, margin),
        (size - margin, margin),
        (int(size / 2), margin + height)
    ]
    
    path = QPainterPath()
    path.moveTo(points[0][0], points[0][1])
    for point in points[1:]:
        path.lineTo(point[0], point[1])
    path.closeSubpath()
    
    painter.drawPath(path)


if __name__ == "__main__":
    # Создаем приложение Qt
    app = QApplication(sys.argv)
    
    # Проверяем существование директории для иконок
    if not os.path.exists(ICONS_DIR):
        os.makedirs(ICONS_DIR)
        print(f"Создана директория для иконок: {ICONS_DIR}")
    
    # Создаем иконки
    icons_to_create = [
        ('file', draw_file_icon),
        ('chart', draw_chart_icon),
        ('data', draw_data_icon),
        ('settings', draw_settings_icon),
        ('down-arrow', draw_down_arrow_icon)
    ]
    
    for name, draw_func in icons_to_create:
        create_icon(name, draw_func)
    
    print("Все иконки созданы успешно!")