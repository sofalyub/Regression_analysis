from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QComboBox, QFileDialog, QTableWidget, QTableWidgetItem, 
                           QTabWidget, QScrollArea, QGridLayout, QSizePolicy, QFrame,
                           QHeaderView, QRadioButton, QCheckBox, QSpacerItem, QTextEdit,
                           QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from ui.styles import COLORS, FONTS, set_font, set_widget_style, create_gradient_button


class FileSelectionWidget(QWidget):
    """
    Виджет для выбора файла Excel
    """
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Основной layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Метка для отображения выбранного файла
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("""
            padding: 8px; 
            border: 1px solid #BDBDBD; 
            border-radius: 4px;
            background-color: white;
        """)
        layout.addWidget(self.file_label, 1)
        
        # Кнопка для выбора файла
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #26A69A;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
            QPushButton:pressed {
                background-color: #00796B;
            }
        """)
        self.browse_button.setMinimumWidth(120)
        self.browse_button.clicked.connect(self.select_file)
        layout.addWidget(self.browse_button)
        
        self.setLayout(layout)
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл Excel", "", "Excel файлы (*.xlsx *.xls)")
        if file_path:
            self.file_label.setText(file_path)
            self.file_selected.emit(file_path)


class SheetSelectionWidget(QWidget):
    """
    Виджет для выбора листа в файле Excel
    """
    sheet_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Основной layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Метка
        label = QLabel("Выберите лист:")
        set_font(label, 'body')
        layout.addWidget(label)
        
        # Выпадающий список листов
        self.sheet_combo = QComboBox()
        self.sheet_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                selection-background-color: #1976D2;
                selection-color: white;
                min-height: 30px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #BDBDBD;
                selection-background-color: #1976D2;
                selection-color: white;
                background-color: white;
            }
        """)
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_selected)
        layout.addWidget(self.sheet_combo, 1)
        
        self.setLayout(layout)
    
    def update_sheets(self, sheets):
        """
        Обновление списка доступных листов
        
        Args:
            sheets (list): Список доступных листов
        """
        self.sheet_combo.clear()
        if sheets:
            self.sheet_combo.addItems(sheets)
            # Автоматически выбираем первый лист и генерируем сигнал выбора
            self.sheet_combo.setCurrentIndex(0)
            self.sheet_selected.emit(sheets[0])
    
    def on_sheet_selected(self, sheet_name):
        """
        Обработчик выбора листа
        
        Args:
            sheet_name (str): Имя выбранного листа
        """
        if sheet_name:
            self.sheet_selected.emit(sheet_name)


class ColumnSelectionWidget(QWidget):
    """
    Виджет для выбора столбцов для регрессии
    """
    columns_selected = pyqtSignal(list, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Секция выбора X (независимых переменных)
        x_layout = QVBoxLayout()
        x_label = QLabel("Независимые переменные (X):")
        x_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        x_label.setStyleSheet(f"color: {COLORS['primary']};")
        x_layout.addWidget(x_label)
        
        self.x_combo = QComboBox()
        self.x_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: #1976D2;
                selection-color: white;
                font-size: 11pt;
                min-height: 35px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #BDBDBD;
                selection-background-color: #1976D2;
                selection-color: white;
                background-color: white;
                font-size: 11pt;
            }
        """)
        x_layout.addWidget(self.x_combo)
        
        layout.addLayout(x_layout)
        
        # Добавляем небольшой отступ
        layout.addSpacing(10)
        
        # Секция выбора Y (зависимой переменной)
        y_layout = QVBoxLayout()
        y_label = QLabel("Зависимая переменная (Y):")
        y_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        y_label.setStyleSheet(f"color: {COLORS['primary']};")
        y_layout.addWidget(y_label)
        
        self.y_combo = QComboBox()
        self.y_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: #1976D2;
                selection-color: white;
                font-size: 11pt;
                min-height: 35px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #BDBDBD;
                selection-background-color: #1976D2;
                selection-color: white;
                background-color: white;
                font-size: 11pt;
            }
        """)
        y_layout.addWidget(self.y_combo)
        
        layout.addLayout(y_layout)
        
        # Добавляем отступ перед кнопкой
        layout.addSpacing(20)
        
        # Кнопка для расчета регрессии
        button_layout = QHBoxLayout()
        self.calculate_button = QPushButton("Рассчитать регрессию")
        self.calculate_button.setMinimumHeight(45)
        self.calculate_button.setMinimumWidth(250)
        self.calculate_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        create_gradient_button(self.calculate_button, COLORS['primary'], COLORS['primary_dark'])
        self.calculate_button.clicked.connect(self.on_calculate)
        button_layout.addStretch(1)
        button_layout.addWidget(self.calculate_button)
        button_layout.addStretch(1)
        
        layout.addLayout(button_layout)
        
        # Добавляем растягивающийся пробел в конце
        layout.addStretch(1)
        
        self.setLayout(layout)
    
    def update_columns(self, columns):
        """
        Обновление списка доступных столбцов
        
        Args:
            columns (list): Список доступных столбцов
        """
        self.x_combo.clear()
        self.y_combo.clear()
        
        if columns:
            # Сортируем столбцы для более удобного выбора
            sorted_columns = sorted(columns)
            
            # Для выбора независимой переменной (X)
            self.x_combo.addItems(sorted_columns)
            
            # Для выбора зависимой переменной (Y)
            self.y_combo.addItems(sorted_columns)
            
            # Если есть хотя бы два столбца, устанавливаем первый столбец как X и второй как Y
            if len(sorted_columns) >= 2:
                self.x_combo.setCurrentIndex(0)
                self.y_combo.setCurrentIndex(1)
    
    def on_calculate(self):
        """
        Обработчик нажатия кнопки расчета регрессии
        """
        x_column = self.x_combo.currentText()
        y_column = self.y_combo.currentText()
        
        if x_column and y_column:
            self.columns_selected.emit([x_column], y_column)


class MultipleColumnSelectionWidget(QWidget):
    """
    Виджет для выбора нескольких столбцов для множественной регрессии
    """
    columns_selected = pyqtSignal(list, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.selected_x_columns = []
    
    def setup_ui(self):
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Секция выбора X (независимых переменных)
        x_label = QLabel("Независимые переменные (X):")
        x_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        x_label.setStyleSheet(f"color: {COLORS['primary']};")
        layout.addWidget(x_label)
        
        # Используем таблицу с чекбоксами
        self.x_list = QTableWidget()
        self.x_list.setColumnCount(2)
        self.x_list.setHorizontalHeaderLabels(["Столбец", "Выбрано"])
        self.x_list.horizontalHeader().setStretchLastSection(True)
        self.x_list.setMinimumHeight(200)
        self.x_list.setStyleSheet("""
            QTableWidget {
                gridline-color: #E0E0E0;
                selection-background-color: #E3F2FD;
                selection-color: #212121;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 11pt;
                background-color: white;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #212121;
            }
            QHeaderView::section {
                background-color: #EEEEEE;
                padding: 6px;
                border: 1px solid #BDBDBD;
                border-width: 0 1px 1px 0;
                font-weight: bold;
                color: #424242;
            }
        """)
        layout.addWidget(self.x_list)
        
        # Добавляем небольшой отступ
        layout.addSpacing(10)
        
        # Секция выбора Y (зависимой переменной)
        y_layout = QVBoxLayout()
        y_label = QLabel("Зависимая переменная (Y):")
        y_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        y_label.setStyleSheet(f"color: {COLORS['primary']};")
        y_layout.addWidget(y_label)
        
        self.y_combo = QComboBox()
        self.y_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                selection-background-color: #1976D2;
                selection-color: white;
                font-size: 11pt;
                min-height: 35px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #BDBDBD;
                selection-background-color: #1976D2;
                selection-color: white;
                background-color: white;
                font-size: 11pt;
            }
        """)
        y_layout.addWidget(self.y_combo)
        
        layout.addLayout(y_layout)
        
        # Добавляем отступ перед кнопкой
        layout.addSpacing(20)
        
        # Кнопка для расчета регрессии
        button_layout = QHBoxLayout()
        self.calculate_button = QPushButton("Рассчитать множественную регрессию")
        self.calculate_button.setMinimumHeight(45)
        self.calculate_button.setMinimumWidth(300)
        self.calculate_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        create_gradient_button(self.calculate_button, COLORS['primary'], COLORS['primary_dark'])
        self.calculate_button.clicked.connect(self.on_calculate)
        button_layout.addStretch(1)
        button_layout.addWidget(self.calculate_button)
        button_layout.addStretch(1)
        
        layout.addLayout(button_layout)
        
        # Добавляем растягивающийся пробел в конце
        layout.addStretch(1)
        
        self.setLayout(layout)
    
    def update_columns(self, columns):
        """
        Обновление списка доступных столбцов
        
        Args:
            columns (list): Список доступных столбцов
        """
        self.x_list.setRowCount(0)
        self.y_combo.clear()
        self.selected_x_columns = []
        
        if not columns:
            return
        
        # Сортируем столбцы для более удобного выбора
        sorted_columns = sorted(columns)
        
        # Заполняем таблицу X
        self.x_list.setRowCount(len(sorted_columns))
        for i, column in enumerate(sorted_columns):
            # Имя столбца
            item = QTableWidgetItem(column)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.x_list.setItem(i, 0, item)
            
            # Чекбокс для выбора
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.x_list.setItem(i, 1, checkbox_item)
        
        # Устанавливаем размеры столбцов
        self.x_list.setColumnWidth(0, 300)  # Первый столбец с именами фиксированной ширины
        
        # Заполняем комбобокс Y
        self.y_combo.addItems(sorted_columns)
        
        # По умолчанию выбираем первый столбец как Y и автоматически отмечаем два следующих столбца как X
        if len(sorted_columns) >= 3:
            self.y_combo.setCurrentIndex(0)
            
            # Отмечаем два следующих столбца как X
            if self.x_list.rowCount() > 1:
                self.x_list.item(1, 1).setCheckState(Qt.Checked)
            if self.x_list.rowCount() > 2:
                self.x_list.item(2, 1).setCheckState(Qt.Checked)
    
    def on_calculate(self):
        """
        Обработчик нажатия кнопки расчета регрессии
        """
        # Собираем выбранные столбцы X
        x_columns = []
        for i in range(self.x_list.rowCount()):
            if self.x_list.item(i, 1).checkState() == Qt.Checked:
                x_columns.append(self.x_list.item(i, 0).text())
        
        y_column = self.y_combo.currentText()
        
        # Проверяем, что выбраны хотя бы 2 переменные X и одна переменная Y
        if len(x_columns) >= 2 and y_column:
            self.columns_selected.emit(x_columns, y_column)


class ResultsWidget(QWidget):
    """
    Виджет для отображения результатов регрессии
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Сохраняем данные для отчета
        self.equation = ""
        self.statistics = {}
        self.interpretation = {}
        self.plots = []
        self.model_type = "Линейная регрессия"
        
        self.setup_ui()
    
    def setup_ui(self):
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавляем панель инструментов
        tool_layout = QHBoxLayout()
        tool_layout.setContentsMargins(10, 10, 10, 5)
        
        # Кнопка для сохранения отчета
        self.save_report_button = QPushButton("Сохранить отчет")
        self.save_report_button.setIcon(QIcon("ui/icons/file.png"))
        self.save_report_button.setMinimumHeight(40)
        self.save_report_button.setMinimumWidth(200)
        self.save_report_button.setStyleSheet("""
            QPushButton {
                background-color: #26A69A;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00897B;
            }
            QPushButton:pressed {
                background-color: #00796B;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        self.save_report_button.setEnabled(False)  # По умолчанию отключена
        self.save_report_button.clicked.connect(self.on_save_report)
        
        tool_layout.addStretch(1)
        tool_layout.addWidget(self.save_report_button)
        
        layout.addLayout(tool_layout)
        
        # Создаем вкладки для различных результатов
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #BDBDBD;
                background-color: #FFFFFF;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #EEEEEE;
                color: #757575;
                border: 1px solid #BDBDBD;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                min-width: 120px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #1976D2;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: #E0E0E0;
            }
        """)
        
        # Вкладка с уравнением регрессии
        self.equation_tab = QWidget()
        equation_layout = QVBoxLayout(self.equation_tab)
        
        # Заменяем QLabel на QTextEdit для лучшего отображения длинных уравнений
        self.equation_text = QTextEdit()
        self.equation_text.setReadOnly(True)
        self.equation_text.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: white;
                color: black;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
        """)
        self.equation_text.setMinimumHeight(180)  # Увеличиваем минимальную высоту
        equation_layout.addWidget(self.equation_text)
        
        self.tab_widget.addTab(self.equation_tab, "Уравнение")
        
        # Вкладка со статистикой
        self.stats_tab = QScrollArea()
        self.stats_tab.setWidgetResizable(True)
        self.stats_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.stats_tab.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
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
        """)
        self.stats_content = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_content)
        self.stats_layout.setAlignment(Qt.AlignTop)
        self.stats_layout.setContentsMargins(15, 15, 15, 15)
        self.stats_layout.setSpacing(10)
        self.stats_tab.setWidget(self.stats_content)
        self.tab_widget.addTab(self.stats_tab, "Статистика")
        
        # Вкладка с интерпретацией
        self.interpretation_tab = QScrollArea()
        self.interpretation_tab.setWidgetResizable(True)
        self.interpretation_tab.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
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
        """)
        self.interpretation_content = QWidget()
        self.interpretation_layout = QVBoxLayout(self.interpretation_content)
        self.interpretation_layout.setAlignment(Qt.AlignTop)
        self.interpretation_layout.setContentsMargins(15, 15, 15, 15)
        self.interpretation_layout.setSpacing(10)
        self.interpretation_tab.setWidget(self.interpretation_content)
        self.tab_widget.addTab(self.interpretation_tab, "Интерпретация")
        
        # Вкладка с графиками
        self.plots_tab = QScrollArea()
        self.plots_tab.setWidgetResizable(True)
        self.plots_tab.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
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
        """)
        self.plots_content = QWidget()
        self.plots_layout = QVBoxLayout(self.plots_content)
        self.plots_layout.setAlignment(Qt.AlignTop)
        self.plots_layout.setContentsMargins(15, 15, 15, 15)
        self.plots_layout.setSpacing(20)
        self.plots_tab.setWidget(self.plots_content)
        self.tab_widget.addTab(self.plots_tab, "Графики")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def set_equation(self, equation):
        """
        Устанавливает уравнение регрессии с улучшенным форматированием
        
        Args:
            equation (str): Уравнение регрессии
        """
        # Сохраняем уравнение для отчета
        self.equation = equation
        
        # Основной стиль для всего уравнения
        html_style = """
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                color: #000000; /* Черный цвет для всего текста */
                line-height: 1.6;
                padding: 10px;
            }
            .equation {
                text-align: center;
                margin: 15px 0;
            }
            .operator {
                padding: 0 5px;
                color: #000000;
            }
            .variable {
                font-style: italic;
            }
            .coefficient {
                font-weight: bold;
            }
        """
        
        # Заменяем математические операторы и добавляем структуру
        # Используем HTML-форматирование для более гибкого контроля
        equation_parts = []
        
        # Разделяем уравнение на части по операторам
        raw_parts = equation.replace(" + ", "|||+|||").replace(" - ", "|||-|||").split("|||")
        
        for i, part in enumerate(raw_parts):
            if part.startswith("+"):
                equation_parts.append(f'<span class="operator">+</span>')
                part = part[1:].strip()
            elif part.startswith("-"):
                equation_parts.append(f'<span class="operator">-</span>')
                part = part[1:].strip()
            
            # Добавляем оставшуюся часть
            if i == 0:  # Первая часть (Y = ...)
                equation_parts.append(f'<span class="variable">{part}</span>')
            else:
                # Разделяем на коэффициент и переменную, если возможно
                if "*" in part:
                    coef, var = part.split("*", 1)
                    equation_parts.append(f'<span class="coefficient">{coef.strip()}</span> × <span class="variable">{var.strip()}</span>')
                else:
                    equation_parts.append(f'<span class="variable">{part}</span>')
        
        # Собираем все вместе
        formatted_equation = "".join(equation_parts)
        
        # Добавляем переносы строк для лучшей читаемости
        formatted_equation = formatted_equation.replace('<span class="operator">+</span>', '<br><span class="operator">+</span>')
        formatted_equation = formatted_equation.replace('<span class="operator">-</span>', '<br><span class="operator">-</span>')
        
        # Первый перенос строки не нужен, если он есть
        if formatted_equation.startswith("<br>"):
            formatted_equation = formatted_equation[4:]
        
        # Формируем полный HTML-документ
        html_content = f"""
        <html>
        <head>
        <style>
        {html_style}
        </style>
        </head>
        <body>
        <div class="equation">{formatted_equation}</div>
        </body>
        </html>
        """
        
        # Устанавливаем HTML в текстовый виджет
        self.equation_text.setHtml(html_content)
    
    def set_statistics(self, stats):
        """
        Заполняет вкладку со статистикой
        
        Args:
            stats (dict): Словарь со статистикой регрессии
        """
        # Сохраняем статистику для отчета
        self.statistics = stats
        
        # Очищаем предыдущие данные
        self._clear_layout(self.stats_layout)
        
        # Проверяем на ошибки
        if 'error' in stats:
            error_label = QLabel(f"Ошибка: {stats['error']}")
            error_label.setStyleSheet("color: #D32F2F; font-weight: bold; font-size: 12pt;")
            self.stats_layout.addWidget(error_label)
            self.save_report_button.setEnabled(False)
            return
        
        # Заполняем новыми данными
        self._add_statistics_section(stats.get("Регрессионная статистика", {}), "Регрессионная статистика")
        self._add_statistics_section(stats.get("Дисперсионный анализ", {}), "Дисперсионный анализ")
        self._add_statistics_section(stats.get("Коэффициенты", {}), "Коэффициенты")
        
        # Активируем кнопку сохранения отчета
        self.save_report_button.setEnabled(True)
    
    def set_interpretation(self, interpretation):
        """
        Заполняет вкладку с интерпретацией
        
        Args:
            interpretation (dict): Словарь с интерпретацией результатов регрессии
        """
        # Сохраняем интерпретацию для отчета
        self.interpretation = interpretation
        
        # Очищаем предыдущие данные
        self._clear_layout(self.interpretation_layout)
        
        # Проверяем на ошибки
        if 'error' in interpretation:
            error_label = QLabel(f"Ошибка: {interpretation['error']}")
            error_label.setStyleSheet("color: #D32F2F; font-weight: bold; font-size: 12pt;")
            self.interpretation_layout.addWidget(error_label)
            return
        
        # Заполняем новыми данными
        for section, content in interpretation.items():
            # Заголовок секции
            section_label = QLabel(section)
            section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            section_label.setStyleSheet(f"""
                padding: 8px; 
                background-color: #E3F2FD; 
                border-radius: 4px;
                color: {COLORS['primary']};
            """)
            self.interpretation_layout.addWidget(section_label)
            
            # Содержимое секции
            if isinstance(content, dict):
                for subsection, text in content.items():
                    subsection_label = QLabel(subsection)
                    subsection_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                    subsection_label.setStyleSheet("color: #00695C; margin-top: 8px;")
                    self.interpretation_layout.addWidget(subsection_label)
                    
                    text_label = QLabel(text)
                    text_label.setWordWrap(True)
                    text_label.setFont(QFont("Segoe UI", 10))
                    text_label.setStyleSheet("padding: 5px; margin-left: 15px;")
                    self.interpretation_layout.addWidget(text_label)
            else:
                text_label = QLabel(content)
                text_label.setWordWrap(True)
                text_label.setFont(QFont("Segoe UI", 10))
                text_label.setStyleSheet("padding: 5px; margin-left: 15px;")
                self.interpretation_layout.addWidget(text_label)
            
            # Добавляем разделитель
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            line.setStyleSheet("background-color: #E0E0E0; margin: 10px 0px;")
            self.interpretation_layout.addWidget(line)
        
        # Добавляем растягивающийся пробел в конце
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.interpretation_layout.addWidget(spacer)
    
    def set_plots(self, plot_canvases):
        """
        Заполняет вкладку с графиками
        
        Args:
            plot_canvases (list): Список объектов matplotlib.figure.Figure с графиками
        """
        # Сохраняем графики для отчета
        self.plots = plot_canvases
        
        # Очищаем предыдущие данные
        self._clear_layout(self.plots_layout)
        
        # Проверяем, есть ли графики
        if not plot_canvases:
            no_plots_label = QLabel("Нет доступных графиков")
            no_plots_label.setAlignment(Qt.AlignCenter)
            no_plots_label.setFont(QFont("Segoe UI", 12))
            no_plots_label.setStyleSheet("color: #757575; padding: 20px;")
            self.plots_layout.addWidget(no_plots_label)
            return
        
        # Заполняем новыми графиками
        for i, canvas in enumerate(plot_canvases):
            # Создаем фрейм для графика с увеличенным размером
            plot_frame = QFrame()
            plot_frame.setFrameShape(QFrame.StyledPanel)
            plot_frame.setFrameShadow(QFrame.Raised)
            plot_frame.setMinimumHeight(650)  # Увеличиваем минимальную высоту с 500 до 650
            plot_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #BDBDBD;
                    border-radius: 6px;
                    background-color: white;
                }
            """)
            plot_layout = QVBoxLayout(plot_frame)
            plot_layout.setContentsMargins(10, 10, 10, 10)  # Увеличиваем внутренние отступы
            
            # Устанавливаем размеры графика
            canvas.setMinimumSize(800, 550)  # Увеличиваем минимальную высоту с 450 до 550
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            
            # Добавляем график во фрейм
            plot_layout.addWidget(canvas)
            
            # Добавляем панель инструментов для взаимодействия с графиком
            toolbar = NavigationToolbar2QT(canvas, plot_frame)
            toolbar.setStyleSheet("background-color: #FAFAFA; border-top: 1px solid #EEEEEE;")
            plot_layout.addWidget(toolbar)
            
            # Добавляем фрейм в основной layout
            self.plots_layout.addWidget(plot_frame)
            
            # Добавляем разделитель между графиками
            if i < len(plot_canvases) - 1:
                spacer = QWidget()
                spacer.setFixedHeight(30)  # Увеличиваем расстояние между графиками с 20 до 30
                self.plots_layout.addWidget(spacer)
        
        # Добавляем растягивающийся пробел в конце
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plots_layout.addWidget(spacer)
    
    def set_model_type(self, model_type):
        """
        Устанавливает тип модели регрессии
        
        Args:
            model_type (str): Тип модели регрессии
        """
        self.model_type = model_type
    
    def on_save_report(self):
        """
        Обработчик событий для кнопки сохранения отчета
        """
        try:
            from report_generator import ReportGenerator
            
            # Проверяем, что у нас есть необходимые данные для отчета
            if not self.equation or not self.statistics or not self.interpretation:
                QMessageBox.warning(self, "Предупреждение", "Недостаточно данных для создания отчета")
                return
            
            # Создаем генератор отчетов
            report_gen = ReportGenerator()
            
            # Генерируем и сохраняем отчет
            success = report_gen.generate_report(
                self,
                self.equation,
                self.statistics,
                self.interpretation,
                self.plots,
                self.model_type
            )
            
            if success:
                QMessageBox.information(self, "Успех", "Отчет успешно сохранен")
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить отчет")
        
        except Exception as e:
            print(f"Ошибка при сохранении отчета: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании отчета: {str(e)}")
    
    def _clear_layout(self, layout):
        """
        Очищает все элементы из layout
        
        Args:
            layout (QLayout): Layout для очистки
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sublayout = item.layout()
                if sublayout is not None:
                    self._clear_layout(sublayout)
    
    def _add_statistics_section(self, stats_dict, section_title):
        """
        Добавляет секцию статистики в вкладку статистики
        
        Args:
            stats_dict (dict): Словарь со статистическими данными
            section_title (str): Заголовок секции
        """
        if not stats_dict:
            return
        
        # Заголовок секции
        section_label = QLabel(section_title)
        section_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        section_label.setStyleSheet(f"""
            padding: 8px; 
            background-color: #E3F2FD; 
            border-radius: 4px;
            color: {COLORS['primary']};
        """)
        self.stats_layout.addWidget(section_label)
        
        # Создаем таблицу для отображения данных
        if section_title == "Дисперсионный анализ":
            # Специальная обработка для дисперсионного анализа
            table = QTableWidget()
            headers = ["", "df", "SS", "MS", "F", "Значимость F"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            rows = ["Регрессия", "Остаток", "Итого"]
            table.setRowCount(len(rows))
            table.setVerticalHeaderLabels(rows)
            
            # Устанавливаем политику изменения размеров для таблицы
            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            table.setMinimumHeight(120)  # Достаточно для 3 строк + заголовок
            
            # Применяем стили к таблице
            table.setStyleSheet("""
                QTableWidget {
                    gridline-color: #E0E0E0;
                    selection-background-color: #E3F2FD;
                    selection-color: #212121;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    font-size: 10pt;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 4px;
                }
                QHeaderView::section {
                    background-color: #EEEEEE;
                    padding: 6px;
                    border: 1px solid #BDBDBD;
                    font-weight: bold;
                    color: #424242;
                }
            """)
            
            for i, row_name in enumerate(rows):
                if row_name in stats_dict:
                    row_data = stats_dict[row_name]
                    for j, col_name in enumerate(headers[1:], 1):
                        if col_name in row_data:
                            value = row_data[col_name]
                            display_value = self._format_number(value)
                            item = QTableWidgetItem(display_value)
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                            table.setItem(i, j, item)
            
            # Настройка размеров столбцов и горизонтальной прокрутки
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # Первая колонка фиксированная
            for i in range(1, len(headers)):
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
            
            # Растягиваем таблицу по ширине окна
            table.horizontalHeader().setStretchLastSection(True)
            
            self.stats_layout.addWidget(table)
        
        elif section_title == "Коэффициенты":
            # Специальная обработка для коэффициентов
            table = QTableWidget()
            headers = ["", "Коэффициент", "Стандартная ошибка", "t-статистика", "P-Значение", "Нижние 95%", "Верхние 95%"]
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            rows = list(stats_dict.keys())
            table.setRowCount(len(rows))
            table.setVerticalHeaderLabels(rows)
            
            # Устанавливаем политику изменения размеров для таблицы
            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            table.setMinimumHeight(80 * len(rows))  # Высота зависит от количества строк
            
            # Применяем стили к таблице
            table.setStyleSheet("""
                QTableWidget {
                    gridline-color: #E0E0E0;
                    selection-background-color: #E3F2FD;
                    selection-color: #212121;
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    font-size: 10pt;
                    background-color: white;
                }
                QTableWidget::item {
                    padding: 4px;
                }
                QHeaderView::section {
                    background-color: #EEEEEE;
                    padding: 6px;
                    border: 1px solid #BDBDBD;
                    font-weight: bold;
                    color: #424242;
                }
            """)
            
            for i, row_name in enumerate(rows):
                row_data = stats_dict[row_name]
                for j, col_name in enumerate(headers[1:], 1):
                    if col_name in row_data:
                        value = row_data[col_name]
                        display_value = self._format_number(value)
                        item = QTableWidgetItem(display_value)
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                        
                        # Выделение статистически значимых p-значений
                        if col_name == "P-Значение" and value is not None and value < 0.05:
                            item.setBackground(QColor('#E8F5E9'))  # Светло-зеленый фон для значимых p-значений
                            item.setForeground(QColor('#1B5E20'))  # Темно-зеленый текст
                        
                        table.setItem(i, j, item)
            
            # Настройка размеров столбцов и горизонтальной прокрутки
            table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # Первая колонка фиксированная
            for i in range(1, len(headers)):
                table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
                table.setColumnWidth(i, 120)  # Устанавливаем одинаковую ширину для всех столбцов
            
            # Растягиваем таблицу по ширине окна
            table.horizontalHeader().setStretchLastSection(True)
            
            self.stats_layout.addWidget(table)
        
        else:
            # Общий случай для других секций
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #BDBDBD;
                    border-radius: 4px;
                    background-color: white;
                    padding: 5px;
                }
            """)
            grid = QGridLayout(frame)
            grid.setContentsMargins(10, 10, 10, 10)
            grid.setSpacing(8)
            
            row = 0
            for key, value in stats_dict.items():
                key_label = QLabel(key + ":")
                key_label.setFont(QFont("Segoe UI", 10))
                key_label.setStyleSheet("color: #424242;")
                grid.addWidget(key_label, row, 0)
                
                display_value = self._format_number(value)
                
                value_label = QLabel(display_value)
                value_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                value_label.setStyleSheet("color: #1976D2;")
                grid.addWidget(value_label, row, 1)
                
                row += 1
            
            self.stats_layout.addWidget(frame)
        
        # Добавляем разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0; margin: 10px 0px;")
        self.stats_layout.addWidget(line)

    def _format_number(self, value):
        """
        Форматирует числовое значение для отображения в таблице
        
        Args:
            value: Числовое значение для форматирования
        
        Returns:
            str: Форматированное значение для отображения
        """
        if value is None:
            return ""
        
        if isinstance(value, (int, float)):
            # Специальное форматирование для очень маленьких p-значений
            if 0 < value < 1e-10:
                return "<1,0×10⁻¹⁰"
            elif 0 < value < 0.0001:
                return "<0,0001"
            # Для очень больших чисел используем научную нотацию
            elif abs(value) >= 1e9:
                return f"{value:.2e}"
            # Для больших чисел округляем до целого
            elif abs(value) >= 1e6:
                return f"{value:,.0f}".replace(",", " ")
            # Для чисел среднего размера используем два десятичных знака
            elif abs(value) >= 1000:
                return f"{value:,.2f}".replace(",", " ")
            # Для маленьких чисел используем 4-6 значащих цифр
            elif abs(value) >= 0.001:
                return f"{value:.4f}".replace(".", ",")
            # Для очень маленьких чисел используем научную нотацию
            elif value != 0:
                return f"{value:.4e}".replace(".", ",")
            else:
                return "0"
        else:
            return str(value)