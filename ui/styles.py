"""
Модуль для управления стилями и темами приложения
"""

from PyQt5.QtGui import QFont, QColor, QPalette, QBrush, QLinearGradient
from PyQt5.QtCore import Qt

# Цветовая схема
COLORS = {
    'primary': '#1976D2',  # Основной цвет (синий)
    'primary_light': '#42A5F5',  # Светлый основной
    'primary_dark': '#0D47A1',  # Темный основной
    'secondary': '#26A69A',  # Дополнительный цвет (бирюзовый)
    'secondary_light': '#4DB6AC',  # Светлый дополнительный
    'secondary_dark': '#00796B',  # Темный дополнительный
    'accent': '#FFC107',  # Акцентный цвет (янтарный)
    'text_primary': '#212121',  # Основной текст
    'text_secondary': '#757575',  # Вторичный текст
    'background': '#F5F5F5',  # Фон
    'card_background': '#FFFFFF',  # Фон карточек
    'divider': '#EEEEEE',  # Разделитель
    'error': '#D32F2F',  # Ошибка
    'success': '#388E3C',  # Успех
    'warning': '#FFA000',  # Предупреждение
    'info': '#1976D2'  # Информация
}

# Шрифты
FONTS = {
    'header': QFont('Segoe UI', 12, QFont.Bold),
    'subheader': QFont('Segoe UI', 11, QFont.Normal),
    'body': QFont('Segoe UI', 10),
    'button': QFont('Segoe UI', 10, QFont.Medium),
    'small': QFont('Segoe UI', 9)
}

# Стили для виджетов
WIDGET_STYLES = {
    'main_window': '''
        QMainWindow {
            background-color: #F5F5F5;
        }
    ''',
    
    'tab_widget': '''
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
    ''',
    
    'group_box': '''
        QGroupBox {
            background-color: #FFFFFF;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            margin-top: 16px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #1976D2;
        }
    ''',
    
    'push_button': '''
        QPushButton {
            background-color: #1976D2;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            text-align: center;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #1565C0;
        }
        
        QPushButton:pressed {
            background-color: #0D47A1;
        }
        
        QPushButton:disabled {
            background-color: #BDBDBD;
            color: #757575;
        }
    ''',
    
    'secondary_button': '''
        QPushButton {
            background-color: #26A69A;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            text-align: center;
            font-weight: bold;
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
    ''',
    
    'text_button': '''
        QPushButton {
            background-color: transparent;
            color: #1976D2;
            border: none;
            padding: 8px 16px;
            text-align: center;
            font-weight: bold;
        }
        
        QPushButton:hover {
            color: #1565C0;
            text-decoration: underline;
        }
        
        QPushButton:pressed {
            color: #0D47A1;
        }
        
        QPushButton:disabled {
            color: #BDBDBD;
        }
    ''',
    
    'combo_box': '''
        QComboBox {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
            selection-background-color: #1976D2;
            selection-color: white;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
        }
        
        QComboBox::down-arrow {
            image: url(ui/icons/down-arrow.png);
            width: 12px;
            height: 12px;
        }
        
        QComboBox QAbstractItemView {
            border: 1px solid #BDBDBD;
            border-radius: 0px;
            selection-background-color: #1976D2;
            selection-color: white;
            background-color: white;
        }
    ''',
    
    'line_edit': '''
        QLineEdit {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            padding: 6px;
            background-color: white;
            selection-background-color: #1976D2;
            selection-color: white;
        }
        
        QLineEdit:focus {
            border: 1px solid #1976D2;
        }
    ''',
    
    'label': '''
        QLabel {
            color: #212121;
        }
    ''',
    
    'header_label': '''
        QLabel {
            color: #1976D2;
            font-weight: bold;
            font-size: 14px;
        }
    ''',
    
    'table_widget': '''
        QTableWidget {
            gridline-color: #E0E0E0;
            selection-background-color: #E3F2FD;
            selection-color: #212121;
            border: 1px solid #BDBDBD;
            border-radius: 4px;
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
        
        QHeaderView::section:checked {
            background-color: #E3F2FD;
        }
    ''',
    
    'scroll_area': '''
        QScrollArea {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            background-color: white;
        }
    ''',
    
    'scroll_bar': '''
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
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;
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
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
        }
    ''',
    
    'status_bar': '''
        QStatusBar {
            background-color: #FAFAFA;
            color: #424242;
            border-top: 1px solid #E0E0E0;
        }
    ''',
    
    'frame': '''
        QFrame {
            border: 1px solid #BDBDBD;
            border-radius: 4px;
            background-color: white;
        }
    ''',
    
    'splitter': '''
        QSplitter::handle {
            background-color: #E0E0E0;
        }
        
        QSplitter::handle:horizontal {
            width: 4px;
        }
        
        QSplitter::handle:vertical {
            height: 4px;
        }
        
        QSplitter::handle:hover {
            background-color: #BDBDBD;
        }
    '''
}

def apply_stylesheet(app):
    """
    Применяет единый стиль ко всему приложению
    
    Args:
        app (QApplication): Экземпляр приложения
    """
    # Базовый стиль для всего приложения
    app.setStyle("Fusion")
    
    # Палитра цветов
    palette = QPalette()
    
    # Базовые цвета
    palette.setColor(QPalette.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text_primary']))
    palette.setColor(QPalette.Base, QColor(COLORS['card_background']))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS['divider']))
    palette.setColor(QPalette.ToolTipBase, QColor('white'))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS['text_primary']))
    
    # Цвета для элементов интерфейса
    palette.setColor(QPalette.Button, QColor(COLORS['primary']))
    palette.setColor(QPalette.ButtonText, QColor('white'))
    palette.setColor(QPalette.BrightText, QColor('white'))
    
    # Цвета для выделения
    palette.setColor(QPalette.Highlight, QColor(COLORS['primary_light']))
    palette.setColor(QPalette.HighlightedText, QColor('white'))
    
    # Цвета для неактивных элементов
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(COLORS['text_secondary']))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(COLORS['text_secondary']))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(COLORS['text_secondary']))
    
    # Применяем палитру
    app.setPalette(palette)
    
    # Объединяем все стили в единую строку
    stylesheet = "\n".join(WIDGET_STYLES.values())
    
    # Применяем стили ко всему приложению
    app.setStyleSheet(stylesheet)

def set_widget_style(widget, style_name):
    """
    Устанавливает определенный стиль для конкретного виджета
    
    Args:
        widget (QWidget): Виджет для стилизации
        style_name (str): Имя стиля из WIDGET_STYLES
    """
    if style_name in WIDGET_STYLES:
        widget.setStyleSheet(WIDGET_STYLES[style_name])
    
def set_font(widget, font_name):
    """
    Устанавливает определенный шрифт для виджета
    
    Args:
        widget (QWidget): Виджет для изменения шрифта
        font_name (str): Имя шрифта из FONTS
    """
    if font_name in FONTS:
        widget.setFont(FONTS[font_name])

def create_gradient_button(button, start_color=COLORS['primary'], end_color=COLORS['primary_dark']):
    """
    Создает кнопку с градиентным фоном
    
    Args:
        button (QPushButton): Кнопка для стилизации
        start_color (str): Начальный цвет градиента
        end_color (str): Конечный цвет градиента
    """
    gradient_style = f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 {start_color}, stop:1 {end_color});
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            text-align: center;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                       stop:0 {end_color}, stop:1 {start_color});
        }}
        
        QPushButton:pressed {{
            background: {end_color};
        }}
        
        QPushButton:disabled {{
            background: #BDBDBD;
            color: #757575;
        }}
    """
    button.setStyleSheet(gradient_style)