import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error


class SimpleLinearRegression:
    """
    Класс для выполнения линейной регрессии по методологии из Excel
    """
    
    def __init__(self):
        """
        Инициализация модели линейной регрессии
        """
        self.slope = None  # Коэффициент наклона (Beta1)
        self.intercept = None  # Y-пересечение (Beta0)
        self.r_squared = None  # Коэффициент детерминации R²
        self.adjusted_r_squared = None  # Скорректированный R²
        self.multiple_r = None  # Коэффициент множественной корреляции R
        self.standard_error = None  # Стандартная ошибка
        self.observations = None  # Количество наблюдений
        self.sum_of_squares_regression = None  # Сумма квадратов регрессии
        self.sum_of_squares_residual = None  # Сумма квадратов остатков
        self.sum_of_squares_total = None  # Общая сумма квадратов
        self.f_statistic = None  # F-статистика
        self.f_significance = None  # Значимость F
        self.slope_std_error = None  # Стандартная ошибка коэффициента наклона
        self.intercept_std_error = None  # Стандартная ошибка Y-пересечения
        self.slope_t_stat = None  # t-статистика для коэффициента наклона
        self.intercept_t_stat = None  # t-статистика для Y-пересечения
        self.slope_p_value = None  # P-значение для коэффициента наклона
        self.intercept_p_value = None  # P-значение для Y-пересечения
        self.slope_confidence_interval = None  # Доверительный интервал для коэффициента наклона
        self.intercept_confidence_interval = None  # Доверительный интервал для Y-пересечения
        self.predictions = None  # Предсказанные значения
        self.residuals = None  # Остатки
    
    def fit(self, X, y):
        """
        Обучение модели линейной регрессии
        
        Args:
            X (numpy.ndarray): Массив независимых переменных (предикторов)
            y (numpy.ndarray): Массив зависимой переменной (отклика)
        """
        # Проверяем входные данные
        if X.shape[0] != y.shape[0]:
            raise ValueError("Количество строк в X и y должно совпадать")
        
        # Сохраняем количество наблюдений
        self.observations = X.shape[0]
        
        # Преобразуем X в одномерный массив, если его форма (n, 1)
        if len(X.shape) > 1 and X.shape[1] == 1:
            X = X.flatten()
        
        # Вычисляем средние X и y
        mean_x = np.mean(X)
        mean_y = np.mean(y)
        
        # Вычисляем коэффициенты регрессии по методу наименьших квадратов
        # Формула для slope (Beta1): sum((X - mean_X) * (y - mean_y)) / sum((X - mean_X)^2)
        numerator = np.sum((X - mean_x) * (y - mean_y))
        denominator = np.sum((X - mean_x) ** 2)
        self.slope = numerator / denominator
        
        # Формула для intercept (Beta0): mean_y - slope * mean_x
        self.intercept = mean_y - self.slope * mean_x
        
        # Вычисляем предсказанные значения
        self.predictions = self.intercept + self.slope * X
        
        # Вычисляем остатки
        self.residuals = y - self.predictions
        
        # Вычисляем суммы квадратов
        self.sum_of_squares_total = np.sum((y - mean_y) ** 2)  # SST
        self.sum_of_squares_residual = np.sum(self.residuals ** 2)  # SSE
        self.sum_of_squares_regression = self.sum_of_squares_total - self.sum_of_squares_residual  # SSR
        
        # Вычисляем коэффициент детерминации R²
        self.r_squared = 1 - (self.sum_of_squares_residual / self.sum_of_squares_total)
        
        # Вычисляем скорректированный R²
        if self.observations > 2:  # для линейной регрессии: n - 2 (есть 2 параметра: slope и intercept)
            self.adjusted_r_squared = 1 - ((1 - self.r_squared) * (self.observations - 1) / (self.observations - 2))
        else:
            self.adjusted_r_squared = None
        
        # Вычисляем коэффициент множественной корреляции R
        self.multiple_r = np.sqrt(self.r_squared)
        
        # Вычисляем стандартную ошибку регрессии
        if self.observations > 2:
            self.standard_error = np.sqrt(self.sum_of_squares_residual / (self.observations - 2))
        else:
            self.standard_error = None
        
        # Вычисляем F-статистику
        if self.observations > 2:
            df_regression = 1  # для простой линейной регрессии
            df_residual = self.observations - 2
            ms_regression = self.sum_of_squares_regression / df_regression
            ms_residual = self.sum_of_squares_residual / df_residual
            self.f_statistic = ms_regression / ms_residual
            
            # Вычисляем значимость F (p-value)
            from scipy import stats
            self.f_significance = 1 - stats.f.cdf(self.f_statistic, df_regression, df_residual)
        else:
            self.f_statistic = None
            self.f_significance = None
        
        # Вычисляем стандартные ошибки коэффициентов, t-статистики и p-значения
        if self.observations > 2:
            # Стандартная ошибка для slope
            self.slope_std_error = self.standard_error / np.sqrt(np.sum((X - mean_x) ** 2))
            
            # Стандартная ошибка для intercept
            self.intercept_std_error = self.standard_error * np.sqrt(1/self.observations + (mean_x**2)/np.sum((X - mean_x)**2))
            
            # t-статистики
            self.slope_t_stat = self.slope / self.slope_std_error
            self.intercept_t_stat = self.intercept / self.intercept_std_error
            
            # p-значения
            df = self.observations - 2
            self.slope_p_value = 2 * (1 - stats.t.cdf(abs(self.slope_t_stat), df))
            self.intercept_p_value = 2 * (1 - stats.t.cdf(abs(self.intercept_t_stat), df))
            
            # Доверительные интервалы (95%)
            t_critical = stats.t.ppf(0.975, df)
            self.slope_confidence_interval = (
                self.slope - t_critical * self.slope_std_error,
                self.slope + t_critical * self.slope_std_error
            )
            self.intercept_confidence_interval = (
                self.intercept - t_critical * self.intercept_std_error,
                self.intercept + t_critical * self.intercept_std_error
            )
        else:
            self.slope_std_error = None
            self.intercept_std_error = None
            self.slope_t_stat = None
            self.intercept_t_stat = None
            self.slope_p_value = None
            self.intercept_p_value = None
            self.slope_confidence_interval = None
            self.intercept_confidence_interval = None
    
    def predict(self, X):
        """
        Предсказание значений по модели
        
        Args:
            X (numpy.ndarray): Массив независимых переменных (предикторов)
        
        Returns:
            numpy.ndarray: Предсказанные значения зависимой переменной
        """
        if self.slope is None or self.intercept is None:
            raise ValueError("Модель не обучена. Сначала вызовите метод fit().")
        
        # Преобразуем X в одномерный массив, если его форма (n, 1)
        if len(X.shape) > 1 and X.shape[1] == 1:
            X = X.flatten()
        
        return self.intercept + self.slope * X
    
    def get_equation_string(self):
        """
        Получение строкового представления уравнения регрессии
        
        Returns:
            str: Строковое представление уравнения регрессии
        """
        if self.slope is None or self.intercept is None:
            return "Модель не обучена"
        
        sign = "+" if self.intercept >= 0 else ""
        return f"Y = {self.slope:.6f} * X {sign} {self.intercept:.6f}"
    
    def get_summary(self):
        """
        Получение сводной статистики регрессии, аналогично выводу в Excel
        
        Returns:
            dict: Словарь со сводной статистикой
        """
        if self.slope is None or self.intercept is None:
            return {"error": "Модель не обучена"}
        
        summary = {
            "Регрессионная статистика": {
                "Множественный R": self.multiple_r,
                "R-квадрат": self.r_squared,
                "Нормированный R-квадрат": self.adjusted_r_squared,
                "Стандартная ошибка": self.standard_error,
                "Наблюдения": self.observations
            },
            "Дисперсионный анализ": {
                "Регрессия": {
                    "df": 1,
                    "SS": self.sum_of_squares_regression,
                    "MS": self.sum_of_squares_regression / 1,
                    "F": self.f_statistic,
                    "Значимость F": self.f_significance
                },
                "Остаток": {
                    "df": self.observations - 2,
                    "SS": self.sum_of_squares_residual,
                    "MS": self.sum_of_squares_residual / (self.observations - 2)
                },
                "Итого": {
                    "df": self.observations - 1,
                    "SS": self.sum_of_squares_total
                }
            },
            "Коэффициенты": {
                "Y-пересечение": {
                    "Коэффициент": self.intercept,
                    "Стандартная ошибка": self.intercept_std_error,
                    "t-статистика": self.intercept_t_stat,
                    "P-Значение": self.intercept_p_value,
                    "Нижние 95%": self.intercept_confidence_interval[0] if self.intercept_confidence_interval else None,
                    "Верхние 95%": self.intercept_confidence_interval[1] if self.intercept_confidence_interval else None
                },
                "X": {
                    "Коэффициент": self.slope,
                    "Стандартная ошибка": self.slope_std_error,
                    "t-статистика": self.slope_t_stat,
                    "P-Значение": self.slope_p_value,
                    "Нижние 95%": self.slope_confidence_interval[0] if self.slope_confidence_interval else None,
                    "Верхние 95%": self.slope_confidence_interval[1] if self.slope_confidence_interval else None
                }
            }
        }
        
        return summary
    
    def get_interpretation(self):
        """
        Получение интерпретации результатов регрессии
        
        Returns:
            dict: Словарь с интерпретацией результатов
        """
        if self.slope is None or self.intercept is None:
            return {"error": "Модель не обучена"}
        
        interpretation = {
            "Уравнение регрессии": self.get_equation_string(),
            "Интерпретация коэффициентов": {
                "Y-пересечение": (
                    f"Значение {self.intercept:.6f} представляет ожидаемое значение Y, когда X равен 0. "
                    f"Статистически {'значимо' if self.intercept_p_value < 0.05 else 'незначимо'} "
                    f"(p-значение = {self.intercept_p_value:.6f})."
                ),
                "Коэффициент наклона": (
                    f"Значение {self.slope:.6f} показывает, что при увеличении X на 1 единицу, "
                    f"Y в среднем изменяется на {self.slope:.6f} единиц. "
                    f"Статистически {'значимо' if self.slope_p_value < 0.05 else 'незначимо'} "
                    f"(p-значение = {self.slope_p_value:.6f})."
                )
            },
            "Качество модели": {
                "R-квадрат": (
                    f"Значение {self.r_squared:.6f} показывает, что {self.r_squared*100:.2f}% вариации в Y "
                    f"объясняется моделью. Это говорит о {'высоком' if self.r_squared > 0.7 else 'среднем' if self.r_squared > 0.5 else 'низком'} "
                    f"качестве соответствия модели данным."
                ),
                "F-статистика": (
                    f"F-статистика равна {self.f_statistic:.6f} с p-значением {self.f_significance:.6f}, "
                    f"что {'подтверждает' if self.f_significance < 0.05 else 'не подтверждает'} "
                    f"статистическую значимость модели в целом."
                )
            },
            "Практические выводы": (
                f"На основе данной модели можно сделать вывод, что между X и Y существует "
                f"{'сильная положительная' if self.slope > 0 and self.r_squared > 0.7 else 'сильная отрицательная' if self.slope < 0 and self.r_squared > 0.7 else 'умеренная положительная' if self.slope > 0 and self.r_squared > 0.5 else 'умеренная отрицательная' if self.slope < 0 and self.r_squared > 0.5 else 'слабая положительная' if self.slope > 0 else 'слабая отрицательная'} "
                f"линейная зависимость. Модель {'может' if self.r_squared > 0.5 else 'не может с высокой точностью'} "
                f"быть использована для прогнозирования значений Y по значениям X."
            )
        }
        
        return interpretation