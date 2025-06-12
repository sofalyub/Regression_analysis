"""
Базовый модуль для визуализации с общими функциями и настройками
"""

import matplotlib.pyplot as plt
import numpy as np
import io
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import sys
import traceback
from matplotlib.ticker import FuncFormatter, MaxNLocator, ScalarFormatter

# Общие настройки matplotlib
matplotlib.use('Qt5Agg')
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.size'] = 11
matplotlib.rcParams['axes.titlesize'] = 14
matplotlib.rcParams['axes.labelsize'] = 12

# Проверка наличия дополнительных пакетов
HAS_AXES_GRID = False
try:
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    HAS_AXES_GRID = True
except ImportError:
    pass

HAS_3D = False
try:
    from mpl_toolkits.mplot3d import Axes3D
    HAS_3D = True
except ImportError:
    pass

HAS_SKLEARN = False
try:
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    pass


class BasePlotter:
    """Базовый класс для всех плоттеров с общими утилитами"""
    
    @staticmethod
    def make_multiline_title(title, max_length=40):
        """
        Разбивает длинный заголовок на несколько строк для лучшего отображения
        
        Args:
            title (str): Исходный заголовок
            max_length (int): Максимальная длина строки
        
        Returns:
            str: Многострочный заголовок
        """
        # Если заголовок короткий, возвращаем как есть
        if len(title) <= max_length:
            return title
        
        # Определяем, содержит ли заголовок очень длинные слова
        words = title.split()
        longest_word = max([len(word) for word in words])
        
        # Если в заголовке есть очень длинное слово, уменьшаем его
        if longest_word > max_length * 0.8:
            # Находим длинные слова и добавляем к ним переносы
            processed_words = []
            for word in words:
                if len(word) > max_length * 0.8:
                    # Разбиваем длинное слово на части
                    parts = [word[i:i+max_length//2] for i in range(0, len(word), max_length//2)]
                    processed_words.extend(parts)
                else:
                    processed_words.append(word)
            words = processed_words
        
        # Разбиваем заголовок на строки
        lines = []
        current_line = words[0]
        
        for word in words[1:]:
            # Проверяем, уместится ли слово в текущую строку
            if len(current_line + " " + word) <= max_length:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        
        # Добавляем последнюю строку
        if current_line:
            lines.append(current_line)
        
        # Если получилось слишком много строк, объединяем последние
        if len(lines) > 3:
            # Оставляем только первые 2 строки и объединяем остальные
            combined_rest = " ".join(lines[2:])
            # Если комбинированная строка всё ещё слишком длинная, обрезаем
            if len(combined_rest) > max_length + 3:
                combined_rest = combined_rest[:max_length] + "..."
            
            lines = lines[:2] + [combined_rest]
        
        return "\n".join(lines)
    
    @staticmethod
    def create_figure_with_adjustments(title_length):
        """
        Создает фигуру с оптимизированными размерами и отступами
        
        Args:
            title_length (int): Длина заголовка
        
        Returns:
            tuple: (Figure, Canvas, Axes)
        """
        # Базовый размер
        figsize = (10, 6)
        
        # Если заголовок длинный, увеличиваем ширину
        if title_length > 40:
            figsize = (12, 6)
        if title_length > 60:
            figsize = (14, 6)
        
        fig = Figure(figsize=figsize, dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # Оптимизируем отступы для лучшего использования пространства
        if title_length > 40:
            # Для длинных заголовков увеличиваем верхний отступ
            fig.subplots_adjust(top=0.85, bottom=0.18, left=0.12, right=0.95)
        else:
            fig.subplots_adjust(top=0.9, bottom=0.15, left=0.12, right=0.95)
        
        return fig, canvas, ax
    
    @staticmethod
    def _optimize_axis_format(ax, x_data, y_data):
        """
        Оптимизирует форматирование осей для лучшей читаемости
        
        Args:
            ax: Оси matplotlib
            x_data: Данные по оси X
            y_data: Данные по оси Y
        """
        # Определяем диапазоны значений
        x_min, x_max = np.min(x_data), np.max(x_data)
        y_min, y_max = np.min(y_data), np.max(y_data)
        
        # Создаем форматировщики для больших чисел
        def millions_formatter(x, pos):
            return f'{x/1e6:.1f}M'
        
        def thousands_formatter(x, pos):
            return f'{x/1e3:.1f}K'
        
        # Применяем форматирование для больших чисел
        if np.max(np.abs(y_data)) > 1e6:
            ax.yaxis.set_major_formatter(FuncFormatter(millions_formatter))
        elif np.max(np.abs(y_data)) > 1e3:
            ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))
        
        if np.max(np.abs(x_data)) > 1e6:
            ax.xaxis.set_major_formatter(FuncFormatter(millions_formatter))
        elif np.max(np.abs(x_data)) > 1e3:
            ax.xaxis.set_major_formatter(FuncFormatter(thousands_formatter))
        
        # Для очень больших или маленьких чисел используем научную нотацию
        if np.max(np.abs(x_data)) > 1e8 or (np.min(np.abs(x_data[x_data != 0])) < 1e-4 if np.any(x_data != 0) else False) or \
           np.max(np.abs(y_data)) > 1e8 or (np.min(np.abs(y_data[y_data != 0])) < 1e-4 if np.any(y_data != 0) else False):
            formatter = ScalarFormatter(useMathText=True)
            formatter.set_scientific(True)
            formatter.set_powerlimits((-3, 4))
            
            ax.xaxis.set_major_formatter(formatter)
            ax.yaxis.set_major_formatter(formatter)
            
            # Перемещаем показатель степени для лучшего отображения
            ax.yaxis.get_offset_text().set_position((-0.12, 0))
            ax.xaxis.get_offset_text().set_position((0, -0.12))
        
        # Поворачиваем метки оси X для лучшей читаемости длинных подписей
        plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        # Оптимизируем количество делений на осях
        if len(x_data) > 0:
            x_range = x_max - x_min
            if x_range > 0:
                # Определяем оптимальное количество делений
                if x_max > 1e3:
                    ax.xaxis.set_major_locator(MaxNLocator(6))
                else:
                    ax.xaxis.set_major_locator(MaxNLocator(8))
        
        if len(y_data) > 0:
            y_range = y_max - y_min
            if y_range > 0:
                # Определяем оптимальное количество делений
                if y_max > 1e3:
                    ax.yaxis.set_major_locator(MaxNLocator(6))
                else:
                    ax.yaxis.set_major_locator(MaxNLocator(8))
    
    @staticmethod
    def wrap_text(text, max_width=30):
        """
        Разбивает длинный текст на строки заданной ширины
        
        Args:
            text (str): Исходный текст
            max_width (int): Максимальная ширина строки
            
        Returns:
            str: Многострочный текст
        """
        if len(text) <= max_width:
            return text
                
        words = text.split()
        lines = []
        current_line = words[0] if words else ""
        
        for word in words[1:]:
            if len(current_line + " " + word) <= max_width:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
                
        return '\n'.join(lines)