import pandas as pd
import os
import numpy as np
import re


class DataLoader:
    """
    Класс для загрузки и подготовки данных из Excel файлов для регрессионного анализа
    """
    
    def __init__(self):
        """
        Инициализация загрузчика данных
        """
        self.data = None
        self.file_path = None
        self.columns = None
        self.sheet_name = None
        self.original_columns = None  # Для хранения исходных имен столбцов
    
    def load_excel(self, file_path, sheet_name=0):
        """
        Загрузка Excel файла
        
        Args:
            file_path (str): Путь к файлу Excel
            sheet_name (str or int, optional): Имя или индекс листа для загрузки. По умолчанию 0.
        
        Returns:
            bool: True если загрузка прошла успешно, иначе False
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                print(f"Файл не найден: {file_path}")
                return False
            
            # Определяем короткое имя файла для логгирования
            file_name = os.path.basename(file_path)
            print(f"Загрузка файла: {file_name}, лист: {sheet_name}")
            
            # Определяем тип файла по имени для применения специфической логики загрузки
            file_type = self._determine_file_type(file_name)
            
            # Пытаемся определить диапазон значимых данных в файле
            data_range = self._find_data_range(file_path, sheet_name, file_type)
            
            if data_range:
                print(f"Найден диапазон данных: {data_range}")
                # Загружаем только значимую часть данных
                skiprows, nrows = data_range
                self.data = pd.read_excel(file_path, sheet_name=sheet_name, 
                                          skiprows=skiprows, nrows=nrows, 
                                          engine='openpyxl')
            else:
                # Если не удалось определить диапазон, загружаем всё
                print("Не удалось определить диапазон данных, загружаем весь лист")
                self.data = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            
            # Сохраняем исходные имена столбцов
            self.original_columns = self.data.columns.tolist()
            print(f"Исходные столбцы: {self.original_columns}")
            
            # Очищаем данные от пустых строк и столбцов
            self._clean_data()
            
            # Назначаем более содержательные имена столбцам
            self._rename_columns(file_type)
            
            # Сохраняем путь к файлу и имя листа
            self.file_path = file_path
            self.sheet_name = sheet_name
            
            # Обновляем список столбцов
            self.columns = self.data.columns.tolist()
            print(f"Итоговые столбцы: {self.columns}")
            
            # Преобразуем столбцы в числовой формат, где возможно
            self._convert_columns_to_numeric()
            
            return True
        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _determine_file_type(self, file_name):
        """
        Определяет тип файла по его имени
        
        Args:
            file_name (str): Имя файла
        
        Returns:
            str: Тип файла ('po_rossii', 'lineynaya', 'mnozhestvennaya' или 'unknown')
        """
        file_name_lower = file_name.lower()
        
        if 'rossii' in file_name_lower or 'россии' in file_name_lower:
            return 'po_rossii'
        elif 'lineynaya' in file_name_lower or 'линейная' in file_name_lower:
            return 'lineynaya'
        elif 'mnozhestvennaya' in file_name_lower or 'множественная' in file_name_lower:
            return 'mnozhestvennaya'
        else:
            return 'unknown'
    
    def _find_data_range(self, file_path, sheet_name, file_type):
        """
        Находит диапазон значимых данных в Excel-файле
        
        Args:
            file_path (str): Путь к файлу Excel
            sheet_name (str or int): Имя или индекс листа
            file_type (str): Тип файла
        
        Returns:
            tuple: (skiprows, nrows) или None если не удалось определить
        """
        try:
            # Загружаем небольшую часть данных для анализа
            preview_data = pd.read_excel(file_path, sheet_name=sheet_name, nrows=50, engine='openpyxl')
            
            # Для известных файлов используем предопределенные диапазоны
            if file_type == 'po_rossii':
                # Ищем начало данных с годами
                for i in range(min(10, len(preview_data))):
                    if isinstance(preview_data.iloc[i, 0], (int, float)) and 2000 <= preview_data.iloc[i, 0] <= 2023:
                        # Нашли строку с годом, определяем количество строк с данными
                        data_rows = sum(1 for j in range(i, len(preview_data)) 
                                       if isinstance(preview_data.iloc[j, 0], (int, float)) 
                                       and 2000 <= preview_data.iloc[j, 0] <= 2023)
                        return i, data_rows
                
                # Если не нашли по годам, ищем по другим признакам
                return self._find_data_range_by_keywords(preview_data)
            
            elif file_type == 'lineynaya':
                # Аналогично для файла линейной регрессии
                for i in range(min(10, len(preview_data))):
                    if isinstance(preview_data.iloc[i, 0], (int, float)) and 2000 <= preview_data.iloc[i, 0] <= 2023:
                        data_rows = sum(1 for j in range(i, len(preview_data)) 
                                       if isinstance(preview_data.iloc[j, 0], (int, float)) 
                                       and 2000 <= preview_data.iloc[j, 0] <= 2023)
                        return i, data_rows
                
                return self._find_data_range_by_keywords(preview_data)
            
            elif file_type == 'mnozhestvennaya':
                # Для множественной регрессии
                for i in range(min(10, len(preview_data))):
                    if isinstance(preview_data.iloc[i, 0], (int, float)) and 2000 <= preview_data.iloc[i, 0] <= 2023:
                        data_rows = sum(1 for j in range(i, len(preview_data)) 
                                       if isinstance(preview_data.iloc[j, 0], (int, float)) 
                                       and 2000 <= preview_data.iloc[j, 0] <= 2023)
                        return i, data_rows
                
                return self._find_data_range_by_keywords(preview_data)
            
            else:
                # Для неизвестных файлов
                return self._find_data_range_by_keywords(preview_data)
        
        except Exception as e:
            print(f"Ошибка при определении диапазона данных: {e}")
            return None
    
    def _find_data_range_by_keywords(self, preview_data):
        """
        Находит диапазон данных, анализируя ключевые слова
        
        Args:
            preview_data (pd.DataFrame): Предварительные данные для анализа
        
        Returns:
            tuple: (skiprows, nrows) или None если не удалось определить
        """
        # Ищем строки с ключевыми словами, указывающими на начало данных
        start_row = -1
        for i in range(len(preview_data)):
            row_str = ' '.join([str(x).lower() for x in preview_data.iloc[i] if not pd.isna(x)])
            if 'год' in row_str or 'денежные доходы' in row_str or 'потребительские расходы' in row_str:
                # Нашли строку заголовка, данные начинаются со следующей строки
                start_row = i + 1
                break
        
        if start_row < 0:
            # Не удалось найти начало данных
            return None
        
        # Определяем количество строк с данными
        end_row = start_row
        empty_rows_count = 0
        
        for i in range(start_row, len(preview_data)):
            row = preview_data.iloc[i]
            if row.isna().all() or all(pd.isna(x) or str(x).strip() == '' for x in row):
                empty_rows_count += 1
                if empty_rows_count >= 2:  # Если встретили две пустые строки подряд, считаем концом данных
                    break
            else:
                empty_rows_count = 0
                end_row = i + 1
        
        data_rows = end_row - start_row
        
        return start_row - 1, data_rows  # -1 чтобы включить заголовки
    
    def _clean_data(self):
        """
        Очищает данные от пустых строк и столбцов
        """
        if self.data is None:
            return
        
        # Удаляем строки, где все значения NaN
        initial_rows = len(self.data)
        self.data = self.data.dropna(how='all')
        dropped_rows = initial_rows - len(self.data)
        print(f"Удалено пустых строк: {dropped_rows}")
        
        # Удаляем столбцы, где все значения NaN
        initial_cols = len(self.data.columns)
        self.data = self.data.dropna(axis=1, how='all')
        dropped_cols = initial_cols - len(self.data.columns)
        print(f"Удалено пустых столбцов: {dropped_cols}")
        
        # Дополнительно удаляем столбцы, которые содержат только NaN или пустые строки
        cols_to_drop = []
        for col in self.data.columns:
            if self.data[col].isna().all() or all(pd.isna(x) or str(x).strip() == '' for x in self.data[col]):
                cols_to_drop.append(col)
        
        if cols_to_drop:
            self.data = self.data.drop(columns=cols_to_drop)
            print(f"Удалено еще {len(cols_to_drop)} пустых столбцов")
    
    def _rename_columns(self, file_type):
        """
        Переименование столбцов на основе содержимого и типа файла
        
        Args:
            file_type (str): Тип файла
        """
        if self.data is None or len(self.data.columns) == 0:
            return
        
        # Словарь для переименования столбцов
        rename_dict = {}
        
        # Определяем, есть ли в столбцах "Unnamed"
        unnamed_columns = [col for col in self.data.columns if 'unnamed' in str(col).lower()]
        
        if unnamed_columns:
            print(f"Обнаружены безымянные столбцы: {unnamed_columns}")
            
            # Специальные правила для известных файлов
            if file_type == 'po_rossii':
                # Для файла по России
                if len(self.data.columns) >= 3:
                    rename_dict = {
                        self.data.columns[0]: "Год",
                        self.data.columns[1]: "Денежные доходы по России",
                        self.data.columns[2]: "Потребительские расходы по России"
                    }
            
            elif file_type == 'lineynaya':
                # Для файла Волгоградской области
                if len(self.data.columns) >= 3:
                    rename_dict = {
                        self.data.columns[0]: "Год",
                        self.data.columns[1]: "Денежные доходы Волгоградской области",
                        self.data.columns[2]: "Потребительские расходы Волгоградской области"
                    }
            
            elif file_type == 'mnozhestvennaya':
                # Для файла множественной регрессии
                
                # Проверяем, сколько столбцов в данных
                if len(self.data.columns) > 10:
                    # Это большой файл с множеством столбцов, первый столбец - год
                    rename_dict[self.data.columns[0]] = "Год"
                    
                    # Далее идут федеральные округа
                    if len(self.data.columns) > 9:
                        fo_names = [
                            "Центральный ФО", "Северо-Западный ФО", "Южный ФО", "Северо-Кавказский ФО",
                            "Приволжский ФО", "Уральский ФО", "Сибирский ФО", "Дальневосточный ФО"
                        ]
                        
                        # Доходы и расходы ФО
                        rename_dict[self.data.columns[1]] = f"Денежные доходы {fo_names[0]}"
                        
                        # Если есть столбец с расходами
                        if len(self.data.columns) > 9:
                            rename_dict[self.data.columns[9]] = f"Потребительские расходы {fo_names[0]}"
        
        # Если ключевые слова в заголовках, используем их
        for i, col in enumerate(self.data.columns):
            col_str = str(col).lower()
            
            if 'год' in col_str and i == 0:
                rename_dict[col] = "Год"
            
            elif 'денежные доходы' in col_str or 'доходы' in col_str:
                if 'волгоградской' in col_str or 'волгоградская' in col_str:
                    rename_dict[col] = "Денежные доходы Волгоградской области"
                elif 'россии' in col_str or 'россия' in col_str:
                    rename_dict[col] = "Денежные доходы по России"
                else:
                    rename_dict[col] = "Денежные доходы"
            
            elif 'потребительские расходы' in col_str or 'расходы' in col_str:
                if 'волгоградской' in col_str or 'волгоградская' in col_str:
                    rename_dict[col] = "Потребительские расходы Волгоградской области"
                elif 'россии' in col_str or 'россия' in col_str:
                    rename_dict[col] = "Потребительские расходы по России"
                else:
                    rename_dict[col] = "Потребительские расходы"
        
        # Для всех оставшихся столбцов без имени, задаем им стандартные имена
        for i, col in enumerate(self.data.columns):
            if col not in rename_dict and ('unnamed' in str(col).lower() or 'столбец' in str(col).lower()):
                if i == 0:
                    rename_dict[col] = "Год"
                else:
                    rename_dict[col] = f"Столбец_{i}"
        
        # Применяем переименование
        if rename_dict:
            print(f"Переименовываем столбцы: {rename_dict}")
            self.data.rename(columns=rename_dict, inplace=True)
    
    def _convert_columns_to_numeric(self):
        """
        Преобразует столбцы в числовой формат, если это возможно
        """
        if self.data is None:
            return
        
        for col in self.data.columns:
            try:
                # Пробуем преобразовать в числовой формат
                numeric_values = pd.to_numeric(self.data[col], errors='coerce')
                # Проверяем, есть ли непустые числовые значения
                if not numeric_values.isna().all():
                    self.data[col] = numeric_values
                    print(f"Столбец {col} преобразован в числовой формат")
            except:
                print(f"Не удалось преобразовать столбец {col} в числовой формат")
    
    def get_available_sheets(self, file_path):
        """
        Получение списка доступных листов в Excel файле
        
        Args:
            file_path (str): Путь к файлу Excel
        
        Returns:
            list: Список имен листов
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            print(f"Доступные листы в файле {file_path}: {sheets}")
            return sheets
        except Exception as e:
            print(f"Ошибка при получении списка листов: {e}")
            return []
    
    def get_numerical_columns(self):
        """
        Получение списка числовых столбцов
        
        Returns:
            list: Список имен числовых столбцов
        """
        if self.data is None:
            print("Данные не загружены")
            return []
        
        numerical_columns = []
        print("Поиск числовых столбцов:")
        
        for col in self.data.columns:
            # Выводим информацию о столбце для отладки
            print(f"Проверяем столбец: {col}, тип: {self.data[col].dtype}")
            
            # Проверяем, не пуст ли столбец
            if self.data[col].isnull().all():
                print(f"Столбец {col} содержит только NaN - пропускаем")
                continue
            
            # Исключаем столбец 'Год', если он имеет соответствующее название
            if 'год' in str(col).lower():
                print(f"Столбец {col} определен как год - пропускаем")
                continue
            
            # Проверяем, содержит ли столбец хотя бы некоторые числовые значения
            if pd.api.types.is_numeric_dtype(self.data[col]) or self.data[col].dtype == 'float64' or self.data[col].dtype == 'int64':
                numerical_columns.append(col)
                print(f"Добавлен числовой столбец: {col}")
            else:
                print(f"Столбец {col} не является числовым - проверяем возможность преобразования")
                # Пробуем преобразовать столбец к числовому типу
                try:
                    # Проверяем, можно ли преобразовать в числа
                    numeric_values = pd.to_numeric(self.data[col], errors='coerce')
                    if not numeric_values.isnull().all():
                        print(f"Столбец {col} можно преобразовать в числовой - добавляем")
                        # Преобразуем столбец в числовой формат
                        self.data[col] = numeric_values
                        numerical_columns.append(col)
                except:
                    print(f"Не удалось преобразовать столбец {col} в числовой формат")
        
        # Если мы не нашли ни одного числового столбца, это странно - добавим все столбцы,
        # которые могут содержать данные
        if not numerical_columns:
            print("Не найдено числовых столбцов. Добавляем все непустые столбцы.")
            for col in self.data.columns:
                if 'год' not in str(col).lower() and not self.data[col].isnull().all():
                    numerical_columns.append(col)
        
        print(f"Найдено числовых столбцов: {len(numerical_columns)}")
        print(f"Числовые столбцы: {numerical_columns}")
        
        return numerical_columns
    
    def get_data_for_regression(self, x_column, y_column):
        """
        Подготовка данных для регрессионного анализа
        
        Args:
            x_column (str): Имя столбца для независимой переменной
            y_column (str): Имя столбца для зависимой переменной
        
        Returns:
            tuple: (X, y) массивы для регрессии
        """
        if self.data is None:
            print("Данные не загружены")
            return None, None
        
        if x_column not in self.data.columns:
            print(f"Столбец X '{x_column}' не найден в данных")
            return None, None
        
        if y_column not in self.data.columns:
            print(f"Столбец Y '{y_column}' не найден в данных")
            return None, None
        
        print(f"Подготовка данных для регрессии: X={x_column}, Y={y_column}")
        
        # Создаем копию данных для работы
        regression_data = self.data[[x_column, y_column]].copy()
        
        # Преобразуем в числовой формат, если это еще не сделано
        regression_data[x_column] = pd.to_numeric(regression_data[x_column], errors='coerce')
        regression_data[y_column] = pd.to_numeric(regression_data[y_column], errors='coerce')
        
        # Удаляем строки с пропущенными значениями в выбранных столбцах
        initial_rows = len(regression_data)
        regression_data = regression_data.dropna()
        dropped_rows = initial_rows - len(regression_data)
        print(f"Удалено строк с пропущенными значениями: {dropped_rows}")
        
        if len(regression_data) == 0:
            print("После удаления NaN не осталось данных для регрессии")
            return None, None
        
        print(f"Итоговые данные для регрессии: {len(regression_data)} строк")
        print(regression_data.head())
        
        # Преобразуем в массивы numpy для регрессии
        X = regression_data[x_column].values.reshape(-1, 1)
        y = regression_data[y_column].values
        
        return X, y
    
    def get_data_for_multiple_regression(self, x_columns, y_column):
        """
        Подготовка данных для множественной регрессии
        
        Args:
            x_columns (list): Список имен столбцов для независимых переменных
            y_column (str): Имя столбца для зависимой переменной
        
        Returns:
            tuple: (X, y) массивы для множественной регрессии
        """
        if self.data is None:
            print("Данные не загружены")
            return None, None
        
        # Проверяем существование столбцов
        missing_columns = [col for col in x_columns + [y_column] if col not in self.data.columns]
        if missing_columns:
            print(f"Следующие столбцы не найдены в данных: {missing_columns}")
            return None, None
        
        print(f"Подготовка данных для множественной регрессии: X={x_columns}, Y={y_column}")
        
        # Создаем DataFrame с нужными столбцами
        columns_to_use = x_columns + [y_column]
        regression_data = self.data[columns_to_use].copy()
        
        # Преобразуем в числовой формат, если это еще не сделано
        for col in columns_to_use:
            regression_data[col] = pd.to_numeric(regression_data[col], errors='coerce')
        
        # Удаляем строки с пропущенными значениями
        initial_rows = len(regression_data)
        regression_data = regression_data.dropna()
        dropped_rows = initial_rows - len(regression_data)
        print(f"Удалено строк с пропущенными значениями: {dropped_rows}")
        
        if len(regression_data) == 0:
            print("После удаления NaN не осталось данных для регрессии")
            return None, None
        
        print(f"Итоговые данные для множественной регрессии: {len(regression_data)} строк")
        print(regression_data.head())
        
        # Преобразуем в массивы numpy для регрессии
        X = regression_data[x_columns].values
        y = regression_data[y_column].values
        
        return X, y
    
    def get_years_column(self):
        """
        Получение столбца с годами, если он присутствует
        
        Returns:
            numpy.ndarray: Массив с годами или None, если столбец не найден
        """
        if self.data is None:
            return None
        
        # Ищем столбец 'Год' или подобный
        year_column = None
        for col in self.data.columns:
            if 'год' in str(col).lower():
                year_column = col
                break
        
        if year_column is not None and not self.data[year_column].isna().all():
            return self.data[year_column].values
        
        return None
    
    def get_column_data(self, column_name):
        """
        Получение данных из указанного столбца
        
        Args:
            column_name (str): Имя столбца
        
        Returns:
            pandas.Series: Данные из столбца
        """
        if self.data is None or column_name not in self.data.columns:
            return None
        
        return self.data[column_name]