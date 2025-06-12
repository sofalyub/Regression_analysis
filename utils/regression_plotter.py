"""
Модуль для построения графиков линейной регрессии
"""

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import traceback
from utils.base_plotter import BasePlotter


class RegressionPlotter(BasePlotter):
    """
    Класс для построения графиков линейной регрессии
    """
    
    @staticmethod
    def create_linear_regression_plot(X, y, model, x_label="X", y_label="Y", title="Линейная регрессия"):
        """
        Создание графика линейной регрессии
        
        Args:
            X (numpy.ndarray): Массив независимой переменной
            y (numpy.ndarray): Массив зависимой переменной
            model: Модель линейной регрессии
            x_label (str): Подпись оси X
            y_label (str): Подпись оси Y
            title (str): Заголовок графика
        
        Returns:
            matplotlib.figure.Figure: Объект фигуры с графиком
        """
        try:
            # Создаем заголовок с переносом строки для длинных названий
            title_length = len(title)
            multiline_title = RegressionPlotter.make_multiline_title(title)
            
            # Создаем фигуру с адаптивными размерами
            fig, canvas, ax = RegressionPlotter.create_figure_with_adjustments(title_length)
            
            # Сортируем данные для построения линии регрессии
            X_flat = X.flatten() if len(X.shape) > 1 else X
            
            # Проверяем данные на NaN
            valid_indices = ~np.isnan(X_flat) & ~np.isnan(y)
            X_valid = X_flat[valid_indices]
            y_valid = y[valid_indices]
            
            if len(X_valid) == 0:
                ax.text(0.5, 0.5, "Недостаточно данных для построения графика", 
                        ha='center', va='center', transform=ax.transAxes)
                return canvas
            
            sorted_indices = np.argsort(X_valid)
            sorted_X = X_valid[sorted_indices]
            
            # Определяем подходящий размер маркеров в зависимости от количества точек
            marker_size = max(20, min(100, 2000 / len(X_valid)))
            
            # Строим точки данных с полупрозрачностью
            scatter = ax.scatter(X_valid, y_valid, color='blue', alpha=0.7, 
                                 marker='o', s=marker_size, label='Данные', edgecolors='navy')
            
            # Строим линию регрессии
            try:
                # Создаем более гладкую линию регрессии с большим количеством точек
                line_x = np.linspace(np.min(X_valid) * 0.98, np.max(X_valid) * 1.02, 100)
                line_y = model.predict(line_x.reshape(-1, 1))
                
                # Строим линию регрессии
                line, = ax.plot(line_x, line_y, color='red', linewidth=2.5, 
                                label='Линия регрессии', zorder=3)
                
                # Добавляем уравнение регрессии и коэффициент детерминации
                # Форматируем числа в российском стиле (запятые вместо точек для десятичных)
                slope_str = f"{model.slope:.4f}".replace('.', ',')
                intercept_str = f"{model.intercept:.4f}".replace('.', ',')
                r2_str = f"{model.r_squared:.4f}".replace('.', ',')
                
                equation = f"y = {slope_str}x + {intercept_str}"
                r_squared = f"R² = {r2_str}"
                
                # Размещаем информацию в рамке
                text_box = ax.text(0.02, 0.95, equation + '\n' + r_squared, 
                                   transform=ax.transAxes, fontsize=12, 
                                   verticalalignment='top', 
                                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
            except Exception as e:
                print(f"Ошибка при построении линии регрессии: {e}")
                ax.text(0.05, 0.95, "Ошибка при построении линии регрессии", 
                        transform=ax.transAxes, fontsize=12, verticalalignment='top', color='red')
            
            # Настраиваем оси и заголовок
            # Создаем многострочные метки осей для длинных названий
            x_label_text = RegressionPlotter.make_multiline_title(x_label, 40)
            y_label_text = RegressionPlotter.make_multiline_title(y_label, 40)
                
            ax.set_xlabel(x_label_text, fontweight='bold')
            ax.set_ylabel(y_label_text, fontweight='bold')
            
            # Устанавливаем многострочный заголовок
            ax.set_title(multiline_title, fontweight='bold', pad=20)
            
            # Настройка сетки
            ax.grid(True, linestyle='--', alpha=0.7, zorder=0)
            
            # Настройка границ графика с отступами для лучшей читаемости
            x_margin = (np.max(X_valid) - np.min(X_valid)) * 0.05
            y_margin = (np.max(y_valid) - np.min(y_valid)) * 0.05
            ax.set_xlim(np.min(X_valid) - x_margin, np.max(X_valid) + x_margin)
            ax.set_ylim(np.min(y_valid) - y_margin, np.max(y_valid) + y_margin)
            
            # Добавляем легенду
            ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True)
            
            # Оптимизируем форматирование осей
            RegressionPlotter._optimize_axis_format(ax, X_valid, y_valid)
            
            return canvas
        
        except Exception as e:
            print(f"Ошибка при создании графика линейной регрессии: {e}")
            # Создаем пустой график с сообщением об ошибке
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Ошибка при создании графика: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas
    
    @staticmethod
    def create_residuals_plot(X, y, model, x_label="Прогнозируемые значения", y_label="Остатки", title="График остатков"):
        """
        Создание графика остатков
        
        Args:
            X (numpy.ndarray): Массив независимой переменной
            y (numpy.ndarray): Массив зависимой переменной
            model: Модель регрессии
            x_label (str): Подпись оси X
            y_label (str): Подпись оси Y
            title (str): Заголовок графика
        
        Returns:
            matplotlib.figure.Figure: Объект фигуры с графиком
        """
        try:
            # Создаем заголовок с переносом строки для длинных названий
            title_length = len(title)
            multiline_title = RegressionPlotter.make_multiline_title(title)
            
            # Создаем фигуру с адаптивными размерами
            fig, canvas, ax = RegressionPlotter.create_figure_with_adjustments(title_length)
            
            # Проверяем данные на NaN
            X_flat = X.flatten() if len(X.shape) > 1 else X
            valid_indices = ~np.isnan(X_flat) & ~np.isnan(y)
            X_valid = X_flat[valid_indices].reshape(-1, 1)
            y_valid = y[valid_indices]
            
            if len(X_valid) == 0:
                ax.text(0.5, 0.5, "Недостаточно данных для построения графика остатков", 
                        ha='center', va='center', transform=ax.transAxes)
                return canvas
            
            try:
                # Получаем предсказанные значения
                predictions = model.predict(X_valid)
                
                # Вычисляем остатки
                residuals = y_valid - predictions
                
                # Определяем подходящий размер маркеров
                marker_size = max(20, min(80, 2000 / len(X_valid)))
                
                # Строим точки остатков с цветовой градацией по абсолютному значению остатка
                scatter = ax.scatter(predictions, residuals, 
                                    c=np.abs(residuals), cmap='coolwarm', 
                                    s=marker_size, alpha=0.7, edgecolors='darkgreen')
                
                # Добавляем цветовую шкалу
                try:
                    cb = fig.colorbar(scatter, ax=ax, pad=0.01)
                    cb.set_label('|Остаток|')
                except Exception as e:
                    print(f"Не удалось добавить цветовую шкалу: {e}")
                
                # Добавляем горизонтальную линию на уровне y=0
                ax.axhline(y=0, color='red', linestyle='-', linewidth=2, zorder=3)
                
                # Добавляем статистику остатков
                mean_residual = np.mean(residuals)
                std_residual = np.std(residuals)
                
                stats_text = (f"Среднее значение остатков: {mean_residual:.4f}\n"
                             f"Стандартное отклонение: {std_residual:.4f}")
                
                # Размещаем информацию в рамке
                text_box = ax.text(0.02, 0.95, stats_text, 
                                  transform=ax.transAxes, fontsize=11, 
                                  verticalalignment='top', 
                                  bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
                
                # Добавляем гистограмму остатков справа, если доступен make_axes_locatable
                from utils.base_plotter import HAS_AXES_GRID, make_axes_locatable
                if HAS_AXES_GRID:
                    try:
                        divider = make_axes_locatable(ax)
                        ax_histy = divider.append_axes("right", 1.2, pad=0.1)
                        ax_histy.hist(residuals, bins=min(20, len(residuals)//5 + 2), 
                                    orientation='horizontal', color='green', alpha=0.6)
                        ax_histy.axhline(y=0, color='red', linestyle='-', linewidth=2)
                        ax_histy.set_xticks([])
                        ax_histy.set_yticks([])
                        ax_histy.spines['right'].set_visible(False)
                        ax_histy.spines['top'].set_visible(False)
                        ax_histy.spines['bottom'].set_visible(False)
                    except Exception as e:
                        print(f"Не удалось добавить гистограмму: {e}")
                
            except Exception as e:
                print(f"Ошибка при построении графика остатков: {e}")
                ax.text(0.5, 0.5, f"Ошибка при построении графика остатков: {str(e)}", 
                        ha='center', va='center', transform=ax.transAxes, color='red')
            
            # Настраиваем оси и заголовок
            # Создаем многострочные метки осей для длинных названий
            x_label_text = RegressionPlotter.make_multiline_title(x_label, 40)
            y_label_text = RegressionPlotter.make_multiline_title(y_label, 40)
                
            ax.set_xlabel(x_label_text, fontweight='bold')
            ax.set_ylabel(y_label_text, fontweight='bold')
            
            # Устанавливаем многострочный заголовок
            ax.set_title(multiline_title, fontweight='bold', pad=20)
            
            # Настройка сетки
            ax.grid(True, linestyle='--', alpha=0.7, zorder=0)
            
            # Устанавливаем симметричные границы по Y относительно нуля
            max_abs_residual = max(abs(np.max(residuals)), abs(np.min(residuals)))
            y_margin = max_abs_residual * 0.1
            ax.set_ylim(-max_abs_residual - y_margin, max_abs_residual + y_margin)
            
            # Оптимизируем форматирование осей
            RegressionPlotter._optimize_axis_format(ax, predictions, residuals)
            
            return canvas
        
        except Exception as e:
            print(f"Ошибка при создании графика остатков: {e}")
            # Создаем пустой график с сообщением об ошибке
            fig = Figure(figsize=(10, 6))
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Ошибка при создании графика остатков: {str(e)}", 
                    ha='center', va='center', transform=ax.transAxes, color='red')
            return canvas