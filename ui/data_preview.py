from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QSizePolicy, QFrame, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
import pandas as pd


class DataPreviewWidget(QWidget):
    """
    Виджет для предварительного просмотра данных из Excel-файла
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Таблица для отображения данных
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
                selection-color: #212121;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 10pt;
                background-color: white;
                alternate-background-color: #F5F5F5;
            }
            
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #F0F0F0;
            }
            
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #212121;
            }
            
            QHeaderView::section {
                background-color: #EEEEEE;
                padding: 8px;
                border: 1px solid #BDBDBD;
                font-weight: bold;
                color: #424242;
            }
            
            QHeaderView::section:checked {
                background-color: #E3F2FD;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                min-height: 30px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            
            QScrollBar:horizontal {
                border: none;
                background: #F5F5F5;
                height: 10px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background: #BDBDBD;
                min-width: 30px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #9E9E9E;
            }
        """)
        layout.addWidget(self.data_table)
        
        # Добавляем информационную метку
        self.info_label = QLabel("Нет данных для отображения")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setFont(QFont("Segoe UI", 11))
        self.info_label.setStyleSheet("color: #757575; padding: 10px;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
    
    def display_data(self, data, max_rows=20):
        """
        Отображение данных из DataFrame в таблице
        
        Args:
            data (pandas.DataFrame): DataFrame с данными
            max_rows (int, optional): Максимальное количество строк для отображения
        """
        if data is None or data.empty:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.data_table.hide()
            self.info_label.setText("Нет данных для отображения")
            self.info_label.show()
            return
        
        # Показываем таблицу и скрываем информационную метку
        self.data_table.show()
        
        # Создаем копию данных для обработки
        display_data = data.copy()
        
        # Удаляем пустые строки и столбцы
        display_data = display_data.dropna(how='all')
        display_data = display_data.dropna(axis=1, how='all')
        
        # Удаляем строки, где все числовые значения равны 0 или NaN
        numeric_cols = display_data.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            non_zero_rows = ~((display_data[numeric_cols] == 0) | display_data[numeric_cols].isna()).all(axis=1)
            display_data = display_data[non_zero_rows]
        
        # Определяем количество строк и столбцов
        num_rows = min(len(display_data), max_rows)
        num_cols = len(display_data.columns)
        
        # Обновляем информационную метку
        if len(display_data) > max_rows:
            self.info_label.setText(f"Показано {max_rows} из {len(display_data)} строк")
            self.info_label.show()
        else:
            self.info_label.setText(f"Показано {len(display_data)} строк")
            self.info_label.show()
        
        # Настраиваем таблицу
        self.data_table.setRowCount(num_rows)
        self.data_table.setColumnCount(num_cols)
        
        # Устанавливаем заголовки столбцов
        self.data_table.setHorizontalHeaderLabels(display_data.columns)
        
        # Добавляем номера строк (индексы)
        indices = display_data.index[:num_rows].astype(str)
        self.data_table.setVerticalHeaderLabels(indices)
        
        # Заполняем таблицу данными
        for i in range(num_rows):
            for j in range(num_cols):
                value = display_data.iloc[i, j]
                
                # Форматируем значение для отображения
                if pd.isna(value):
                    display_value = ""
                elif isinstance(value, (int, float)):
                    # Форматируем число для более компактного отображения
                    if abs(value) >= 1e9:
                        display_value = f"{value:.2e}"  # Научная нотация для очень больших чисел
                    elif abs(value) >= 1e6:
                        display_value = f"{value:,.1f}M".replace(".0M", "M").replace(",", " ")  # Миллионы
                    elif abs(value) >= 1e3:
                        display_value = f"{value:,.1f}K".replace(".0K", "K").replace(",", " ")  # Тысячи
                    elif abs(value) < 0.01 and value != 0:
                        display_value = f"{value:.2e}"  # Научная нотация для очень маленьких чисел
                    elif value == int(value):
                        display_value = f"{int(value):,}".replace(",", " ")  # Целые числа без дробной части
                    else:
                        # Ограничиваем количество знаков после запятой
                        display_value = f"{value:,.4f}".rstrip('0').rstrip('.').replace(",", " ")
                else:
                    display_value = str(value)
                
                # Создаем элемент таблицы
                item = QTableWidgetItem(display_value)
                
                # Выравнивание: числа - по правому краю, текст - по левому
                if isinstance(value, (int, float)):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # Применяем разное цветовое оформление в зависимости от типа данных
                if isinstance(value, (int, float)) and not pd.isna(value):
                    # Подсветка числовых значений
                    if value > 0:
                        # Положительные числа - светло-синий фон
                        item.setBackground(QBrush(QColor(240, 248, 255)))
                        # Для больших положительных значений
                        if value > 1000:
                            item.setForeground(QBrush(QColor(25, 118, 210)))  # Синий текст
                    elif value < 0:
                        # Отрицательные числа - светло-красный фон
                        item.setBackground(QBrush(QColor(255, 235, 238)))
                        item.setForeground(QBrush(QColor(198, 40, 40)))  # Красный текст
                elif pd.isna(value):
                    # Пустые ячейки - светло-серый фон
                    item.setBackground(QBrush(QColor(245, 245, 245)))
                
                # Добавляем элемент в таблицу
                self.data_table.setItem(i, j, item)
        
        # Настраиваем горизонтальную прокрутку
        self.data_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Настраиваем размеры столбцов - делаем их адаптивными
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Устанавливаем оптимальные размеры столбцов на основе содержимого
        self.data_table.resizeColumnsToContents()
        
        # Для широкого набора данных устанавливаем фиксированную ширину столбцов
        if num_cols > 3:
            for i in range(num_cols):
                curr_width = self.data_table.columnWidth(i)
                # Ограничиваем максимальную ширину столбца
                if curr_width > 200:
                    self.data_table.setColumnWidth(i, 200)
                # Устанавливаем минимальную ширину столбца
                elif curr_width < 80:
                    self.data_table.setColumnWidth(i, 80)
        
        # Устанавливаем высоту строк
        for i in range(num_rows):
            self.data_table.setRowHeight(i, 30)  # 30 пикселей для каждой строки