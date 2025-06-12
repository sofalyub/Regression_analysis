from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTabWidget, QMessageBox, QSplitter, QApplication, QStatusBar,
                             QGroupBox, QFrame, QTableWidget, QTabBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
import sys
import numpy as np
import os
import pandas as pd
import traceback

try:
    from sklearn.preprocessing import StandardScaler
except ImportError:
    print("Warning: StandardScaler not available. Some visualizations may be limited.")

from ui.widgets import (FileSelectionWidget, SheetSelectionWidget, ColumnSelectionWidget, 
                        MultipleColumnSelectionWidget, ResultsWidget)
from ui.data_preview import DataPreviewWidget
from utils.data_loader import DataLoader
from utils.regression_plotter import RegressionPlotter
from utils.multireg_plotter import MultiRegPlotter
from utils.base_plotter import HAS_3D, HAS_SKLEARN
from models.linear_regression import SimpleLinearRegression
from models.multiple_regression import MultipleRegression
from ui.styles import apply_stylesheet, set_widget_style, set_font, FONTS, create_gradient_button


class RegressionApp(QMainWindow):
    """
    Основной класс приложения для анализа регрессии
    """
    
    def __init__(self):
        super().__init__()
        
        self.data_loader = DataLoader()
        self.linear_model = SimpleLinearRegression()
        self.multiple_model = MultipleRegression()
        
        self.setup_ui()
        self.setup_connections()
        self.apply_styles()
        
        self.setWindowTitle("Анализ регрессии")
        self.setGeometry(100, 100, 1400, 900)  # Увеличиваем размер окна по умолчанию
        self.show()
    
    def setup_ui(self):
        """
        Настройка пользовательского интерфейса
        """
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # Увеличиваем отступы
        main_layout.setSpacing(10)  # Увеличиваем расстояние между элементами
        
        # Создаем главные вкладки
        self.main_tabs = QTabWidget()
        
        # Вкладка 1: Загрузка данных и предпросмотр
        self.data_tab = QWidget()
        data_tab_layout = QVBoxLayout(self.data_tab)
        data_tab_layout.setContentsMargins(12, 12, 12, 12)  # Добавляем отступы внутри вкладки
        
        # Секция выбора файла
        file_group = QGroupBox("Выбор файла")
        file_layout = QVBoxLayout(file_group)
        file_layout.setContentsMargins(15, 20, 15, 15)  # Увеличиваем внутренние отступы
        
        file_label = QLabel("Выберите файл Excel для анализа:")
        file_layout.addWidget(file_label)
        
        self.file_selection = FileSelectionWidget()
        file_layout.addWidget(self.file_selection)
        
        self.sheet_selection = SheetSelectionWidget()
        file_layout.addWidget(self.sheet_selection)
        
        data_tab_layout.addWidget(file_group)
        
        # Секция предпросмотра данных
        preview_group = QGroupBox("Предварительный просмотр данных")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setContentsMargins(15, 20, 15, 15)
        
        self.data_preview = DataPreviewWidget()
        preview_layout.addWidget(self.data_preview)
        
        data_tab_layout.addWidget(preview_group, 1)  # Растягиваем по высоте
        
        self.main_tabs.addTab(self.data_tab, "Данные")
        
        # Вкладка 2: Анализ (линейная и множественная регрессия)
        self.analysis_tab = QWidget()
        analysis_tab_layout = QVBoxLayout(self.analysis_tab)
        analysis_tab_layout.setContentsMargins(12, 12, 12, 12)
        
        # Вкладки для типов регрессии
        self.regression_tabs = QTabWidget()
        
        # Вкладка для линейной регрессии
        linear_tab = QWidget()
        linear_layout = QVBoxLayout(linear_tab)
        linear_layout.setContentsMargins(15, 15, 15, 15)
        
        linear_group = QGroupBox("Параметры линейной регрессии")
        linear_inner_layout = QVBoxLayout(linear_group)
        
        self.linear_selection = ColumnSelectionWidget()
        linear_inner_layout.addWidget(self.linear_selection)
        
        linear_layout.addWidget(linear_group)
        
        # Добавляем растягивающийся пробел
        linear_layout.addStretch(1)
        
        self.regression_tabs.addTab(linear_tab, "Линейная регрессия")
        
        # Вкладка для множественной регрессии
        multiple_tab = QWidget()
        multiple_layout = QVBoxLayout(multiple_tab)
        multiple_layout.setContentsMargins(15, 15, 15, 15)
        
        multiple_group = QGroupBox("Параметры множественной регрессии")
        multiple_inner_layout = QVBoxLayout(multiple_group)
        
        self.multiple_selection = MultipleColumnSelectionWidget()
        multiple_inner_layout.addWidget(self.multiple_selection)
        
        multiple_layout.addWidget(multiple_group)
        
        # Добавляем растягивающийся пробел
        multiple_layout.addStretch(1)
        
        self.regression_tabs.addTab(multiple_tab, "Множественная регрессия")
        
        # Увеличиваем ширину вкладки для множественной регрессии
        multiple_tab_index = 1  # Индекс вкладки "Множественная регрессия" (обычно 1)
        tab_bar = self.regression_tabs.tabBar()
        tab_bar.setTabButton(multiple_tab_index, QTabBar.RightSide, None)  # Убираем кнопки справа
        
        # Применяем специальный стиль для увеличения ширины только второй вкладки
        self.regression_tabs.setStyleSheet("""
            QTabBar::tab:last {
                min-width: 200px;  /* Увеличенная ширина для последней вкладки */
            }
        """)
        
        analysis_tab_layout.addWidget(self.regression_tabs)
        
        self.main_tabs.addTab(self.analysis_tab, "Анализ")
        
        # Вкладка 3: Результаты
        self.results_tab = QWidget()
        results_tab_layout = QVBoxLayout(self.results_tab)
        results_tab_layout.setContentsMargins(12, 12, 12, 12)
        
        results_group = QGroupBox("Результаты регрессионного анализа")
        results_inner_layout = QVBoxLayout(results_group)
        
        self.results_widget = ResultsWidget()
        results_inner_layout.addWidget(self.results_widget)
        
        results_tab_layout.addWidget(results_group)
        
        self.main_tabs.addTab(self.results_tab, "Результаты")
        
        # Добавляем вкладки в основной layout
        main_layout.addWidget(self.main_tabs)
        
        # Добавляем статусную строку
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к работе")
    
    def setup_connections(self):
        """
        Настройка связей между виджетами
        """
        # Связываем выбор файла с загрузкой списка листов
        self.file_selection.file_selected.connect(self.load_sheets)
        
        # Связываем выбор листа с загрузкой данных
        self.sheet_selection.sheet_selected.connect(self.load_data)
        
        # Связываем выбор столбцов с расчетом регрессии
        self.linear_selection.columns_selected.connect(self.calculate_linear_regression)
        self.multiple_selection.columns_selected.connect(self.calculate_multiple_regression)
    
    def apply_styles(self):
        """
        Применение стилей к элементам интерфейса
        """
        # Стили для вкладок
        set_widget_style(self.main_tabs, 'tab_widget')
        # Не применяем общий стиль к regression_tabs, так как мы уже установили специальный стиль
        set_widget_style(self.results_widget.tab_widget, 'tab_widget')
        
        # Стили для группы элементов
        for group in self.findChildren(QGroupBox):
            set_widget_style(group, 'group_box')
            set_font(group, 'header')
        
        # Стили для таблиц
        for table in self.findChildren(QTableWidget):
            set_widget_style(table, 'table_widget')
        
        # Стили для фреймов
        for frame in self.findChildren(QFrame):
            set_widget_style(frame, 'frame')
        
        # Стили для полосы состояния
        set_widget_style(self.status_bar, 'status_bar')
        set_font(self.status_bar, 'body')
        
        # Стили для всех кнопок расчета регрессии
        create_gradient_button(self.linear_selection.calculate_button, '#1976D2', '#0D47A1')
        create_gradient_button(self.multiple_selection.calculate_button, '#1976D2', '#0D47A1')
        
        # Стиль для кнопки выбора файла
        create_gradient_button(self.file_selection.browse_button, '#26A69A', '#00796B')
        
        # Шрифты для меток
        for label in self.findChildren(QLabel):
            set_font(label, 'body')
    
    def load_sheets(self, file_path):
        """
        Загрузка списка листов из выбранного файла
        
        Args:
            file_path (str): Путь к файлу Excel
        """
        # Проверяем существование файла
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Ошибка", f"Файл не найден: {file_path}")
            self.status_bar.showMessage("Файл не найден")
            return
        
        self.status_bar.showMessage(f"Загрузка листов из файла: {file_path}")
        sheets = self.data_loader.get_available_sheets(file_path)
        
        if sheets:
            self.sheet_selection.update_sheets(sheets)
            self.status_bar.showMessage(f"Файл загружен: {file_path}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить листы из выбранного файла")
            self.status_bar.showMessage("Ошибка при загрузке файла")
    
    def load_data(self, sheet_name):
        """
        Загрузка данных из выбранного листа
        
        Args:
            sheet_name (str): Имя выбранного листа
        """
        file_path = self.file_selection.file_label.text()
        if file_path == "Файл не выбран":
            return
        
        self.status_bar.showMessage(f"Загрузка данных из листа: {sheet_name}")
        
        # Выводим информацию о загрузке
        print(f"Загрузка данных из файла: {file_path}, лист: {sheet_name}")
        
        success = self.data_loader.load_excel(file_path, sheet_name)
        
        if success:
            # Выводим первые несколько строк данных для отладки
            print(f"Загружено данных: {len(self.data_loader.data)} строк")
            print("Первые 5 строк данных:")
            print(self.data_loader.data.head())
            print("Столбцы:", self.data_loader.data.columns.tolist())
            
            # Отображаем данные в виджете предпросмотра
            self.data_preview.display_data(self.data_loader.data)
            
            # Получаем числовые столбцы для регрессии
            columns = self.data_loader.get_numerical_columns()
            print(f"Найдено числовых столбцов: {len(columns)}")
            print("Числовые столбцы:", columns)
            
            if not columns:
                QMessageBox.warning(self, "Предупреждение", 
                                   "Не найдено числовых столбцов для анализа. Проверьте формат данных в файле.")
                self.status_bar.showMessage("Не найдено числовых столбцов для анализа")
                return
            
            # Обновляем списки столбцов в виджетах выбора
            self.linear_selection.update_columns(columns)
            self.multiple_selection.update_columns(columns)
            
            # Переключаемся на вкладку анализа
            self.main_tabs.setCurrentIndex(1)
            
            self.status_bar.showMessage(f"Данные загружены из листа: {sheet_name}")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить данные из выбранного листа")
            self.status_bar.showMessage("Ошибка при загрузке данных")
    
    def calculate_linear_regression(self, x_columns, y_column):
        """
        Расчет линейной регрессии
        
        Args:
            x_columns (list): Список имен столбцов для независимых переменных
            y_column (str): Имя столбца для зависимой переменной
        """
        if len(x_columns) != 1:
            QMessageBox.warning(self, "Ошибка", "Для линейной регрессии требуется ровно один столбец X")
            return
        
        x_column = x_columns[0]
        
        # Проверяем, что x и y не одинаковы
        if x_column == y_column:
            QMessageBox.warning(self, "Ошибка", "Переменные X и Y не должны быть одинаковыми")
            return
        
        self.status_bar.showMessage(f"Расчет линейной регрессии: {x_column} -> {y_column}")
        
        # Получаем данные
        X, y = self.data_loader.get_data_for_regression(x_column, y_column)
        
        if X is None or y is None or len(X) == 0 or len(y) == 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить данные для регрессии. Проверьте наличие числовых значений в выбранных столбцах.")
            self.status_bar.showMessage("Ошибка при получении данных")
            return
        
        try:
            # Обучаем модель
            print(f"Начинаем обучение модели линейной регрессии: {len(X)} наблюдений")
            self.linear_model.fit(X, y)
            
            # Отображаем результаты
            equation = f"{y_column} = {self.linear_model.slope:.6f} * {x_column} + {self.linear_model.intercept:.6f}"
            print(f"Построено уравнение регрессии: {equation}")
            self.results_widget.set_equation(equation)
            
            # Статистика
            summary = self.linear_model.get_summary()
            print(f"Получена статистика: R² = {self.linear_model.r_squared:.6f}")
            self.results_widget.set_statistics(summary)
            
            # Интерпретация
            interpretation = self.linear_model.get_interpretation()
            self.results_widget.set_interpretation(interpretation)
            
            # Графики
            plots = []
            # График линейной регрессии
            regression_plot = RegressionPlotter.create_linear_regression_plot(
                X, y, self.linear_model, 
                x_label=x_column, 
                y_label=y_column, 
                title=f"{x_column} -> {y_column}"
            )
            plots.append(regression_plot)
            
            # График остатков
            residuals_plot = RegressionPlotter.create_residuals_plot(
                X, y, self.linear_model,
                x_label="Прогнозируемые значения",
                y_label="Остатки",
                title=f"График остатков: {x_column} -> {y_column}"
            )
            plots.append(residuals_plot)
            
            self.results_widget.set_plots(plots)
            
            # Переключаемся на вкладку результатов
            self.main_tabs.setCurrentIndex(2)
            
            self.status_bar.showMessage(f"Линейная регрессия рассчитана: R² = {self.linear_model.r_squared:.4f}")
            
        except Exception as e:
            print(f"Ошибка при расчете регрессии: {str(e)}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "Ошибка", f"Ошибка при расчете регрессии: {str(e)}")
            self.status_bar.showMessage("Ошибка при расчете регрессии")
    
    def calculate_multiple_regression(self, x_columns, y_column):
        """
        Расчет множественной регрессии с улучшенным отображением графиков
        
        Args:
            x_columns (list): Список имен столбцов для независимых переменных
            y_column (str): Имя столбца для зависимой переменной
        """
        if len(x_columns) < 2:
            QMessageBox.warning(self, "Ошибка", "Для множественной регрессии требуется не менее двух столбцов X")
            return
        
        # Проверяем, что y не входит в x_columns
        if y_column in x_columns:
            QMessageBox.warning(self, "Ошибка", "Зависимая переменная не должна быть в списке независимых переменных")
            return
        
        self.status_bar.showMessage(f"Расчет множественной регрессии: {', '.join(x_columns)} -> {y_column}")
        print(f"Расчет множественной регрессии: {', '.join(x_columns)} -> {y_column}")
        
        # Получаем данные
        X, y = self.data_loader.get_data_for_multiple_regression(x_columns, y_column)
        
        if X is None or y is None or len(X) == 0 or len(y) == 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить данные для регрессии. Проверьте наличие числовых значений в выбранных столбцах.")
            self.status_bar.showMessage("Ошибка при получении данных")
            return
        
        # Проверяем количество наблюдений
        if len(X) <= len(x_columns):
            QMessageBox.warning(self, "Ошибка", f"Недостаточно наблюдений ({len(X)}) для анализа {len(x_columns)} переменных. Необходимо по крайней мере {len(x_columns) + 1} наблюдений.")
            self.status_bar.showMessage("Недостаточно наблюдений для множественной регрессии")
            return
        
        try:
            # Обучаем модель
            print(f"Начинаем обучение модели множественной регрессии: {len(X)} наблюдений, {len(x_columns)} переменных")
            self.multiple_model.fit(X, y, feature_names=x_columns)
            
            # Отображаем результаты
            equation = self.multiple_model.get_equation_string()
            print(f"Построено уравнение регрессии: {equation}")
            self.results_widget.set_equation(equation)
            
            # Статистика
            summary = self.multiple_model.get_summary()
            print(f"Получена статистика: R² = {self.multiple_model.r_squared:.6f}")
            self.results_widget.set_statistics(summary)
            
            # Интерпретация
            interpretation = self.multiple_model.get_interpretation()
            self.results_widget.set_interpretation(interpretation)
            
            # Сортируем предикторы по значимости для лучшей визуализации
            if self.multiple_model.coef_p_values is not None:
                significant_features = []
                feature_importance = [(i, p, x_columns[i]) for i, p in enumerate(self.multiple_model.coef_p_values)]
                sorted_features = sorted(feature_importance, key=lambda x: x[1])  # Сортировка по p-значению
                
                print("Значимость предикторов:")
                for i, p_value, name in sorted_features:
                    significance = "значимый" if p_value < 0.05 else "незначимый"
                    print(f"- {name}: p-значение = {p_value:.6f} ({significance})")
        
            # Формируем базовый заголовок для графиков
            base_title = f"Множественная регрессия: {y_column}"
            
            # Используем улучшенную функцию для создания графиков множественной регрессии
            try:
                # Пробуем использовать новый модуль MultiRegPlotter
                plots = []
                
                # График "Прогноз vs Факт"
                prediction_plot = MultiRegPlotter.create_prediction_vs_actual_plot(
                    X, y, self.multiple_model,
                    y_label=y_column,
                    title=f"{base_title}\nПрогноз vs Факт"
                )
                plots.append(prediction_plot)
                
                # График остатков
                residuals_plot = MultiRegPlotter.create_residuals_plot(
                    X, y, self.multiple_model,
                    y_label=y_column,
                    title=f"{base_title}\nГрафик остатков"
                )
                plots.append(residuals_plot)
                
                # Корреляционная матрица с улучшенным отображением длинных названий
                if X.shape[1] > 1:
                    correlation_plot = MultiRegPlotter.create_correlation_matrix(
                        np.hstack([X, y.reshape(-1, 1)]),
                        feature_names=x_columns + [y_column],
                        title=f"{base_title}\nКорреляционная матрица"
                    )
                    plots.append(correlation_plot)
                
                # 3D график для наиболее значимых признаков (если их достаточно)
                if X.shape[1] >= 2 and HAS_3D and HAS_SKLEARN:
                    try:
                        # Выбираем два наиболее значимых признака
                        significant_indices = []
                        
                        # Если доступны p-значения, выбираем признаки с наименьшими p-значениями
                        if self.multiple_model.coef_p_values is not None:
                            feature_p_values = [(i, p) for i, p in enumerate(self.multiple_model.coef_p_values)]
                            sorted_features = sorted(feature_p_values, key=lambda x: x[1])
                            significant_indices = [i for i, _ in sorted_features[:min(2, len(sorted_features))]]
                        else:
                            # Иначе используем абсолютные значения коэффициентов
                            feature_coefs = [(i, abs(c)) for i, c in enumerate(self.multiple_model.coefficients)]
                            sorted_features = sorted(feature_coefs, key=lambda x: x[1], reverse=True)
                            significant_indices = [i for i, _ in sorted_features[:min(2, len(sorted_features))]]
                        
                        if len(significant_indices) >= 2:
                            x1_index, x2_index = significant_indices[0], significant_indices[1]
                            
                            # Генерируем 3D визуализацию
                            plot_3d = MultiRegPlotter.create_3d_surface_plot(
                                X, y, self.multiple_model,
                                x1_index, x2_index,
                                feature_names=x_columns,
                                y_label=y_column,
                                title=f"{base_title}\n3D визуализация"
                            )
                            plots.append(plot_3d)
                    except Exception as e:
                        print(f"Не удалось создать 3D график: {e}")
                        traceback.print_exc()
                
                # Графики частичных зависимостей для важных признаков
                # Определяем важные признаки по p-значениям или абсолютным значениям коэффициентов
                important_indices = []
                
                if self.multiple_model.coef_p_values is not None:
                    important_indices = [i for i, p_value in enumerate(self.multiple_model.coef_p_values) 
                                        if p_value < 0.05]
                
                # Если не нашли значимых признаков по p-value, берем первые 3 по абсолютному значению коэффициентов
                if not important_indices and self.multiple_model.coefficients is not None:
                    coef_importance = [(i, abs(c)) for i, c in enumerate(self.multiple_model.coefficients)]
                    sorted_coefs = sorted(coef_importance, key=lambda x: x[1], reverse=True)
                    important_indices = [i for i, _ in sorted_coefs[:min(3, len(sorted_coefs))]]
                
                # Создаем график для каждого важного признака
                for idx in important_indices:
                    feature_name = x_columns[idx]
                    partial_plot = MultiRegPlotter.create_partial_dependence_plot(
                        X, y, self.multiple_model,
                        feature_index=idx,
                        feature_name=feature_name,
                        y_label=y_column,
                        title=f"Частичная зависимость для {feature_name}"
                    )
                    plots.append(partial_plot)
                
                self.results_widget.set_plots(plots)
                
            except ImportError:
                # Если новый модуль еще не доступен, используем старую функцию
                plots = RegressionPlotter.create_multiple_regression_plots(
                    X, y, self.multiple_model, 
                    feature_names=x_columns,
                    y_label=y_column,
                    title=base_title
                )
                self.results_widget.set_plots(plots)
            
            # Переключаемся на вкладку результатов
            self.main_tabs.setCurrentIndex(2)
            
            self.status_bar.showMessage(f"Множественная регрессия рассчитана: R² = {self.multiple_model.r_squared:.4f}")
            
        except Exception as e:
            print(f"Ошибка при расчете множественной регрессии: {str(e)}")
            traceback.print_exc()
            QMessageBox.warning(self, "Ошибка", f"Ошибка при расчете множественной регрессии: {str(e)}")
            self.status_bar.showMessage("Ошибка при расчете множественной регрессии")


def run_app():
    """
    Запуск приложения
    """
    app = QApplication(sys.argv)
    
    # Применяем стили ко всему приложению
    apply_stylesheet(app)
    
    window = RegressionApp()
    sys.exit(app.exec_())