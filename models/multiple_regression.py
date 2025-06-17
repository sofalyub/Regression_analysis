import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from scipy import stats


class MultipleRegression:
    """
    Класс для выполнения множественной регрессии по методологии из Excel
    """
    
    def __init__(self):
        """
        Инициализация модели множественной регрессии
        """
        self.coefficients = None  # Коэффициенты модели
        self.intercept = None  # Y-пересечение
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
        self.coef_std_errors = None  # Стандартные ошибки коэффициентов
        self.intercept_std_error = None  # Стандартная ошибка Y-пересечения
        self.coef_t_stats = None  # t-статистики для коэффициентов
        self.intercept_t_stat = None  # t-статистика для Y-пересечения
        self.coef_p_values = None  # P-значения для коэффициентов
        self.intercept_p_value = None  # P-значение для Y-пересечения
        self.coef_confidence_intervals = None  # Доверительные интервалы для коэффициентов
        self.intercept_confidence_interval = None  # Доверительный интервал для Y-пересечения
        self.predictions = None  # Предсказанные значения
        self.residuals = None  # Остатки
        self.feature_names = None  # Имена признаков
    
    def fit(self, X, y, feature_names=None):
        """
        Обучение модели множественной регрессии
        
        Args:
            X (numpy.ndarray): Массив независимых переменных (предикторов)
            y (numpy.ndarray): Массив зависимой переменной (отклика)
            feature_names (list, optional): Список имен признаков. По умолчанию None.
        """
        # Проверяем входные данные
        if X.shape[0] != y.shape[0]:
            raise ValueError("Количество строк в X и y должно совпадать")
        
        # Сохраняем количество наблюдений и количество признаков
        self.observations = X.shape[0]
        n_features = X.shape[1]
        
        # Сохраняем имена признаков
        if feature_names is None:
            self.feature_names = [f"Переменная X {i+1}" for i in range(n_features)]
        else:
            if len(feature_names) != n_features:
                raise ValueError("Количество имен признаков должно совпадать с количеством столбцов в X")
            self.feature_names = feature_names
        
        # Проверка на мультиколлинеарность
        if n_features > 1:
            correlation_matrix = np.corrcoef(X.T)
            # Проверяем абсолютные значения корреляций (исключая диагональ)
            off_diagonal_correlations = np.abs(correlation_matrix[np.triu_indices(n_features, k=1)])
            high_correlations = off_diagonal_correlations > 0.95
            
            if np.any(high_correlations):
                print(f"ПРЕДУПРЕЖДЕНИЕ: Обнаружена высокая корреляция между переменными:")
                for i, j in zip(*np.triu_indices(n_features, k=1)):
                    if abs(correlation_matrix[i, j]) > 0.95:
                        print(f"  {self.feature_names[i]} и {self.feature_names[j]}: {correlation_matrix[i, j]:.4f}")
        
        # Используем LinearRegression из scikit-learn для вычисления коэффициентов
        model = LinearRegression()
        model.fit(X, y)
        
        self.coefficients = model.coef_
        self.intercept = model.intercept_
        
        # Вычисляем предсказанные значения
        self.predictions = model.predict(X)
        
        # Вычисляем остатки
        self.residuals = y - self.predictions
        
        # Вычисляем средние значения
        mean_y = np.mean(y)
        
        # Вычисляем суммы квадратов
        self.sum_of_squares_total = np.sum((y - mean_y) ** 2)  # SST
        self.sum_of_squares_residual = np.sum(self.residuals ** 2)  # SSE
        self.sum_of_squares_regression = self.sum_of_squares_total - self.sum_of_squares_residual  # SSR
        
        # Отладочная информация для сумм квадратов
        print(f"DEBUG Суммы квадратов:")
        print(f"  mean_y = {mean_y}")
        print(f"  sum_of_squares_total = {self.sum_of_squares_total}")
        print(f"  sum_of_squares_residual = {self.sum_of_squares_residual}")
        print(f"  sum_of_squares_regression = {self.sum_of_squares_regression}")
        print(f"  residuals_min = {np.min(self.residuals)}")
        print(f"  residuals_max = {np.max(self.residuals)}")
        print(f"  residuals_mean = {np.mean(self.residuals)}")
        print(f"  residuals_std = {np.std(self.residuals)}")
        
        # Вычисляем коэффициент детерминации R²
        self.r_squared = 1 - (self.sum_of_squares_residual / self.sum_of_squares_total)
        
        # Вычисляем скорректированный R²
        if self.observations > n_features + 1:
            self.adjusted_r_squared = 1 - ((1 - self.r_squared) * (self.observations - 1) / (self.observations - n_features - 1))
        else:
            self.adjusted_r_squared = None
        
        # Вычисляем коэффициент множественной корреляции R
        self.multiple_r = np.sqrt(self.r_squared)
        
        # Вычисляем стандартную ошибку регрессии
        if self.observations > n_features + 1:
            self.standard_error = np.sqrt(self.sum_of_squares_residual / (self.observations - n_features - 1))
        else:
            self.standard_error = None
        
        # Вычисляем F-статистику
        if self.observations > n_features + 1:
            df_regression = n_features
            df_residual = self.observations - n_features - 1
            ms_regression = self.sum_of_squares_regression / df_regression
            ms_residual = self.sum_of_squares_residual / df_residual
            self.f_statistic = ms_regression / ms_residual
            
            # Вычисляем значимость F (p-value)
            # Используем survival function для более точных результатов с очень большими F-статистиками
            self.f_significance = stats.f.sf(self.f_statistic, df_regression, df_residual)
            
            # Проверка на числовую стабильность
            if np.isnan(self.f_significance) or np.isinf(self.f_significance):
                print(f"ПРЕДУПРЕЖДЕНИЕ: Проблема с числовой стабильностью F-статистики")
                print(f"  f_statistic = {self.f_statistic}")
                print(f"  df_regression = {df_regression}")
                print(f"  df_residual = {df_residual}")
                # Устанавливаем минимальное значение
                self.f_significance = 1e-10
            elif self.f_significance < 1e-10:
                print(f"ПРЕДУПРЕЖДЕНИЕ: Очень маленькое p-значение F-статистики: {self.f_significance}")
                # Ограничиваем минимальное значение для стабильности
                self.f_significance = 1e-10
            
            # Отладочная информация
            print(f"DEBUG F-статистика:")
            print(f"  df_regression = {df_regression}")
            print(f"  df_residual = {df_residual}")
            print(f"  sum_of_squares_regression = {self.sum_of_squares_regression}")
            print(f"  sum_of_squares_residual = {self.sum_of_squares_residual}")
            print(f"  ms_regression = {ms_regression}")
            print(f"  ms_residual = {ms_residual}")
            print(f"  f_statistic = {self.f_statistic}")
            print(f"  f_significance = {self.f_significance}")
        else:
            self.f_statistic = None
            self.f_significance = None
        
        # Вычисляем стандартные ошибки коэффициентов, t-статистики и p-значения
        if self.observations > n_features + 1:
            # Формируем матрицу X с добавленным столбцом единиц для интерсепта
            X_with_intercept = np.column_stack((np.ones(self.observations), X))
            
            # Вычисляем матрицу (X^T X)^(-1)
            X_transpose_X = np.dot(X_with_intercept.T, X_with_intercept)
            try:
                X_transpose_X_inv = np.linalg.inv(X_transpose_X)
            except np.linalg.LinAlgError:
                # Если матрица сингулярная, используем псевдоинверсию
                X_transpose_X_inv = np.linalg.pinv(X_transpose_X)
            
            # Вычисляем стандартные ошибки коэффициентов
            mse = self.sum_of_squares_residual / df_residual
            var_coef = np.diag(X_transpose_X_inv) * mse
            std_errors = np.sqrt(var_coef)
            
            self.intercept_std_error = std_errors[0]
            self.coef_std_errors = std_errors[1:]
            
            # Вычисляем t-статистики
            self.intercept_t_stat = self.intercept / self.intercept_std_error
            self.coef_t_stats = self.coefficients / self.coef_std_errors
            
            # Вычисляем p-значения
            df = self.observations - n_features - 1
            self.intercept_p_value = 2 * (1 - stats.t.cdf(abs(self.intercept_t_stat), df))
            self.coef_p_values = 2 * (1 - stats.t.cdf(abs(self.coef_t_stats), df))
            
            # Вычисляем доверительные интервалы (95%)
            t_critical = stats.t.ppf(0.975, df)
            self.intercept_confidence_interval = (
                self.intercept - t_critical * self.intercept_std_error,
                self.intercept + t_critical * self.intercept_std_error
            )
            self.coef_confidence_intervals = [
                (coef - t_critical * std_err, coef + t_critical * std_err)
                for coef, std_err in zip(self.coefficients, self.coef_std_errors)
            ]
        else:
            self.intercept_std_error = None
            self.coef_std_errors = None
            self.intercept_t_stat = None
            self.coef_t_stats = None
            self.intercept_p_value = None
            self.coef_p_values = None
            self.intercept_confidence_interval = None
            self.coef_confidence_intervals = None
    
    def predict(self, X):
        """
        Предсказание значений по модели
        
        Args:
            X (numpy.ndarray): Массив независимых переменных (предикторов)
        
        Returns:
            numpy.ndarray: Предсказанные значения зависимой переменной
        """
        if self.coefficients is None or self.intercept is None:
            raise ValueError("Модель не обучена. Сначала вызовите метод fit().")
        
        return self.intercept + np.dot(X, self.coefficients)
    
    def get_equation_string(self):
        """
        Получение строкового представления уравнения регрессии
        
        Returns:
            str: Строковое представление уравнения регрессии
        """
        if self.coefficients is None or self.intercept is None:
            return "Модель не обучена"
        
        equation = f"Y = {self.intercept:.6f}"
        
        for i, coef in enumerate(self.coefficients):
            sign = "+" if coef >= 0 else ""
            equation += f" {sign} {coef:.6f} * {self.feature_names[i]}"
        
        return equation
    
    def get_summary(self):
        """
        Получение сводной статистики регрессии, аналогично выводу в Excel
        
        Returns:
            dict: Словарь со сводной статистикой
        """
        if self.coefficients is None or self.intercept is None:
            return {"error": "Модель не обучена"}
        
        n_features = len(self.coefficients)
        
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
                    "df": n_features,
                    "SS": self.sum_of_squares_regression,
                    "MS": self.sum_of_squares_regression / n_features,
                    "F": self.f_statistic,
                    "Значимость F": self.f_significance
                },
                "Остаток": {
                    "df": self.observations - n_features - 1,
                    "SS": self.sum_of_squares_residual,
                    "MS": self.sum_of_squares_residual / (self.observations - n_features - 1)
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
                }
            }
        }
        
        # Добавляем информацию о коэффициентах
        for i, feature_name in enumerate(self.feature_names):
            summary["Коэффициенты"][feature_name] = {
                "Коэффициент": self.coefficients[i],
                "Стандартная ошибка": self.coef_std_errors[i] if self.coef_std_errors is not None else None,
                "t-статистика": self.coef_t_stats[i] if self.coef_t_stats is not None else None,
                "P-Значение": self.coef_p_values[i] if self.coef_p_values is not None else None,
                "Нижние 95%": self.coef_confidence_intervals[i][0] if self.coef_confidence_intervals else None,
                "Верхние 95%": self.coef_confidence_intervals[i][1] if self.coef_confidence_intervals else None
            }
        
        
        return summary
    
    def get_interpretation(self):
        """
        Получение интерпретации результатов множественной регрессии
        
        Returns:
            dict: Словарь с интерпретацией результатов
        """
        if self.coefficients is None or self.intercept is None:
            return {"error": "Модель не обучена"}
        
        interpretation = {
            "Уравнение регрессии": self.get_equation_string(),
            "Интерпретация коэффициентов": {
                "Y-пересечение": (
                    f"Значение {self.intercept:.6f} представляет ожидаемое значение Y, когда все X равны 0. "
                    f"Статистически {'значимо' if self.intercept_p_value < 0.05 else 'незначимо'} "
                    f"(p-значение = {self.intercept_p_value:.6f})."
                )
            },
            "Качество модели": {
                "R-квадрат": (
                    f"Значение {self.r_squared:.6f} показывает, что {self.r_squared*100:.2f}% вариации в Y "
                    f"объясняет моделью. Это говорит о {'высоком' if self.r_squared > 0.7 else 'среднем' if self.r_squared > 0.5 else 'низком'} "
                    f"качестве соответствия модели данным."
                ),
                "Скорректированный R-квадрат": (
                    f"Значение {self.adjusted_r_squared:.6f} учитывает количество предикторов в модели. "
                    f"Это более надёжная оценка качества модели при множественной регрессии."
                ),
                "F-статистика": (
                    f"F-статистика равна {self.f_statistic:.6f} с p-значением {self.f_significance:.6f}, "
                    f"что {'подтверждает' if self.f_significance < 0.05 else 'не подтверждает'} "
                    f"статистическую значимость модели в целом."
                )
            },
            "Значимость переменных": {}
        }
        
        # Добавляем интерпретацию для каждой переменной
        for i, feature_name in enumerate(self.feature_names):
            coef = self.coefficients[i]
            p_value = self.coef_p_values[i] if self.coef_p_values is not None else None
            
            if p_value is not None:
                significance = "значимо" if p_value < 0.05 else "незначимо"
                interpretation["Значимость переменных"][feature_name] = (
                    f"Коэффициент {coef:.6f} показывает, что при увеличении {feature_name} на 1 единицу "
                    f"(при фиксированных значениях других переменных), Y в среднем изменяется на {coef:.6f} единиц. "
                    f"Статистически {significance} (p-значение = {p_value:.6f})."
                )
            else:
                interpretation["Значимость переменных"][feature_name] = (
                    f"Коэффициент {coef:.6f} показывает, что при увеличении {feature_name} на 1 единицу "
                    f"(при фиксированных значениях других переменных), Y в среднем изменяется на {coef:.6f} единиц. "
                    f"Статистическая значимость не может быть оценена."
                )
        
        # Добавляем общий вывод
        interpretation["Практические выводы"] = (
            f"На основе данной модели можно сделать вывод, что модель {'хорошо' if self.r_squared > 0.7 else 'умеренно' if self.r_squared > 0.5 else 'слабо'} "
            f"объясняет вариацию зависимой переменной. "
        )
        
        # Добавляем информацию о наиболее значимых переменных
        if self.coef_p_values is not None:
            significant_features = [self.feature_names[i] for i, p in enumerate(self.coef_p_values) if p < 0.05]
            
            if significant_features:
                interpretation["Практические выводы"] += (
                    f"Наиболее значимыми предикторами являются: {', '.join(significant_features)}. "
                )
            else:
                interpretation["Практические выводы"] += (
                    "Ни один из предикторов не является статистически значимым, что может указывать на проблемы с моделью. "
                )
        
        interpretation["Практические выводы"] += (
            f"Модель {'может' if self.r_squared > 0.5 else 'не может с высокой точностью'} "
            f"быть использована для прогнозирования значений Y по значениям предикторов."
        )
        
        return interpretation