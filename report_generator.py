"""
Модуль для генерации отчетов с результатами регрессионного анализа
"""

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDateTime, Qt
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile
from io import BytesIO
import traceback
import sys

class ReportGenerator:
    def __init__(self):
        # Регистрируем шрифты из папки fonts
        try:
            # Получаем путь к шрифтам (работает и в Python, и в EXE)
            if hasattr(sys, '_MEIPASS'):
                # Если запущено из EXE (PyInstaller)
                base_path = sys._MEIPASS
            else:
                # Если запущено из Python
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            fonts_dir = os.path.join(base_path, 'fonts')
            
            print(f"Базовый путь: {base_path}")
            print(f"Директория со шрифтами: {fonts_dir}")
            
            # Проверяем существование файлов шрифтов
            font_path = os.path.join(fonts_dir, 'DejaVuSans.ttf')
            bold_font_path = os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')
            
            print(f"Путь к обычному шрифту: {font_path}")
            print(f"Путь к жирному шрифту: {bold_font_path}")
            
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Файл шрифта не найден: {font_path}")
            if not os.path.exists(bold_font_path):
                raise FileNotFoundError(f"Файл шрифта не найден: {bold_font_path}")
            
            # Регистрируем шрифты
            pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
            
            print("Шрифты успешно зарегистрированы")
            self.FONT_NAME = 'DejaVuSans'
            self.FONT_NAME_BOLD = 'DejaVuSans-Bold'
            
        except Exception as e:
            print(f"Ошибка при регистрации шрифтов: {str(e)}")
            print("Трассировка ошибки:")
            traceback.print_exc()
            print("Используем встроенный шрифт Times-Roman")
            self.FONT_NAME = 'Times-Roman'
            self.FONT_NAME_BOLD = 'Times-Bold'
        
        # Создаем стили
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            fontName=self.FONT_NAME_BOLD,
            fontSize=16,
            alignment=1,
            spaceAfter=30
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            fontName=self.FONT_NAME_BOLD,
            fontSize=14,
            alignment=0,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            fontName=self.FONT_NAME,
            fontSize=12,
            alignment=0,
            spaceAfter=12
        ))
        self.styles.add(ParagraphStyle(
            name='Equation',
            fontName=self.FONT_NAME,
            fontSize=12,
            alignment=1,
            spaceAfter=12
        ))
        
        # Список временных файлов для удаления
        self.temp_files = []
    
    def _ensure_unicode(self, text):
        """Преобразует текст в Unicode"""
        if isinstance(text, bytes):
            return text.decode('utf-8')
        return str(text)
    
    def _figure_to_image(self, figure_canvas):
        """
        Преобразует matplotlib figure в изображение для PDF
        
        Args:
            figure_canvas: FigureCanvas из matplotlib
        
        Returns:
            str: Путь к временному файлу с изображением или None в случае ошибки
        """
        try:
            # Проверяем, что figure_canvas не None
            if figure_canvas is None:
                print("Предупреждение: figure_canvas is None")
                return None
            
            # Получаем figure из canvas
            figure = figure_canvas.figure
            
            # Проверяем, что figure не None
            if figure is None:
                print("Предупреждение: figure is None")
                return None
            
            # Проверяем, что figure содержит хотя бы один axes
            if not figure.axes:
                print("Предупреждение: figure не содержит axes")
                return None
            
            # Проверяем, что axes содержит данные
            has_data = False
            for ax in figure.axes:
                if ax.lines or ax.collections or ax.images or ax.patches:
                    has_data = True
                    break
            
            if not has_data:
                print("Предупреждение: figure не содержит данных для отображения")
                return None
            
            # Устанавливаем более высокое разрешение для графика
            dpi = 150
            
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.close()
            
            # Сохраняем рисунок во временный файл
            figure.savefig(temp_file.name, format='png', dpi=dpi, bbox_inches='tight')
            
            # Проверяем, что файл создался и не пустой
            if not os.path.exists(temp_file.name) or os.path.getsize(temp_file.name) == 0:
                print("Предупреждение: Временный файл не создался или пустой")
                return None
            
            # Добавляем файл в список для последующего удаления
            self.temp_files.append(temp_file.name)
            
            print(f"График успешно сохранен в {temp_file.name}")
            return temp_file.name
        
        except Exception as e:
            print(f"Ошибка при конвертации графика: {str(e)}")
            traceback.print_exc()
            return None
    
    def _cleanup_temp_files(self):
        """Удаляет все временные файлы"""
        for file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Ошибка при удалении временного файла {file_path}: {str(e)}")
        self.temp_files = []
    
    def generate_report(self, parent_widget, equation, statistics, interpretation, figures, model_type="Линейная регрессия"):
        try:
            print("Начало генерации отчета...")
            
            # Проверяем, есть ли хотя бы какой-то контент для отображения
            has_content = False
            if equation and equation.strip():
                has_content = True
                print("✓ Уравнение предоставлено")
            else:
                print("✗ Уравнение не предоставлено или пусто")
            
            if statistics and len(statistics) > 0:
                has_content = True
                print("✓ Статистика предоставлена")
            else:
                print("✗ Статистика не предоставлена или пуста")
            
            if interpretation and len(interpretation) > 0:
                has_content = True
                print("✓ Интерпретация предоставлена")
            else:
                print("✗ Интерпретация не предоставлена или пуста")
            
            if figures and len(figures) > 0:
                has_content = True
                print("✓ Графики предоставлены")
            else:
                print("✗ Графики не предоставлены или список пуст")
            
            if not has_content:
                print("ПРЕДУПРЕЖДЕНИЕ: Нет контента для отображения в отчете!")
                return False
            
            # Запрашиваем у пользователя место для сохранения отчета
            current_date = QDateTime.currentDateTime().toString("yyyy-MM-dd")
            default_filename = f"Отчет_регрессия_{current_date}.pdf"
            
            file_path, _ = QFileDialog.getSaveFileName(
                parent_widget,
                "Сохранить отчет",
                default_filename,
                "PDF файлы (*.pdf)"
            )
            
            if not file_path:
                print("Пользователь отменил сохранение")
                return False
            
            # Если пользователь не указал расширение .pdf, добавляем его
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            print(f"Путь для сохранения отчета: {file_path}")
            
            try:
                # Создаем PDF документ
                doc = SimpleDocTemplate(
                    file_path,
                    pagesize=landscape(A4),
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )
                print("PDF документ успешно создан")
            except Exception as e:
                print(f"Ошибка при создании PDF документа: {str(e)}")
                raise
            
            print("Создаем элементы отчета...")
            
            # Список элементов для добавления в документ
            elements = []
            # 1. Титульная страница
            elements.append(Paragraph(self._ensure_unicode("Отчет по результатам"), self.styles['CustomTitle']))
            elements.append(Paragraph(self._ensure_unicode(f"Дата создания: {current_date}"), self.styles['CustomNormal']))
            elements.append(Spacer(1, 20))

            # Флаги наличия разделов
            has_equation = equation and equation.strip()
            has_statistics = statistics and len(statistics) > 0 and any(section and len(section) > 0 for section in statistics.values())
            has_interpretation = interpretation and len(interpretation) > 0 and any(
                (isinstance(content, dict) and any(text and str(text).strip() for text in content.values())) or (content and str(content).strip())
                for section, content in interpretation.items() if section != 'error')
            has_figures = figures and len(figures) > 0

            # 2. Уравнение
            if has_equation:
                elements.append(Paragraph(self._ensure_unicode("Уравнение регрессии:"), self.styles['CustomHeading']))
                elements.append(Paragraph(self._ensure_unicode(equation), self.styles['Equation']))
                elements.append(Spacer(1, 20))

            # 3. Статистика
            if has_statistics:
                elements.append(Paragraph(self._ensure_unicode("Статистика регрессии"), self.styles['CustomHeading']))
                
                # Регрессионная статистика
                if "Регрессионная статистика" in statistics:
                    elements.append(Paragraph(self._ensure_unicode("Регрессионная статистика:"), self.styles['CustomNormal']))
                    data = [[self._ensure_unicode("Показатель"), self._ensure_unicode("Значение")]]
                    for key, value in statistics["Регрессионная статистика"].items():
                        if isinstance(value, (int, float)):
                            if key == "Наблюдения":
                                value_str = str(int(value))
                            else:
                                value_str = "{:.4f}".format(value).replace(".", ",")
                        else:
                            value_str = "Н/Д"
                        data.append([self._ensure_unicode(key), self._ensure_unicode(value_str)])
                    
                    table = Table(data, colWidths=[300, 150])
                    table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), self.FONT_NAME),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('PADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                
                # Дисперсионный анализ
                if "Дисперсионный анализ" in statistics:
                    elements.append(Paragraph(self._ensure_unicode("Дисперсионный анализ:"), self.styles['CustomNormal']))
                    
                    # Создаем заголовки с переносом строк
                    headers = [
                        self._ensure_unicode("Источник"),
                        self._ensure_unicode("df"),
                        self._ensure_unicode("SS"),
                        self._ensure_unicode("MS"),
                        self._ensure_unicode("F"),
                        self._ensure_unicode("Значимость\nF")
                    ]
                    
                    data = [headers]
                    for key in ["Регрессия", "Остаток", "Итого"]:
                        if key in statistics["Дисперсионный анализ"]:
                            row = [self._ensure_unicode(key)]
                            for col in ["df", "SS", "MS", "F", "Значимость F"]:
                                value = statistics["Дисперсионный анализ"][key].get(col, "")
                                if isinstance(value, (int, float)):
                                    if col == "df":
                                        value_str = str(int(value))
                                    elif col == "Значимость F":
                                        # Специальное форматирование для p-значений
                                        if value < 1e-10:
                                            value_str = "<1,0×10⁻¹⁰"
                                        elif value < 0.0001:
                                            value_str = "<0,0001"
                                        else:
                                            value_str = "{:.4f}".format(value).replace(".", ",")
                                    elif col == "F":
                                        value_str = "{:.4f}".format(value).replace(".", ",")
                                    elif col == "SS" and abs(value) > 1000000:
                                        # Для больших значений SS используем научную нотацию
                                        value_str = "{:.2e}".format(value).replace(".", ",").replace("e", "×10^")
                                    else:
                                        value_str = "{:.2f}".format(value).replace(".", ",")
                                else:
                                    value_str = ""
                                row.append(self._ensure_unicode(value_str))
                            data.append(row)
                    
                    # Увеличиваем ширину колонки SS и других колонок
                    table = Table(data, colWidths=[150, 80, 140, 120, 100, 120])
                    table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), self.FONT_NAME),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Уменьшаем размер шрифта
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('PADDING', (0, 0), (-1, -1), 8),  # Увеличиваем отступы
                        ('WORDWRAP', (0, 0), (-1, -1), True),  # Включаем перенос слов
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 20))
                
                # Коэффициенты
                if "Коэффициенты" in statistics:
                    # Проверяем, есть ли данные для отображения
                    coefficients_data = statistics["Коэффициенты"]
                    if coefficients_data and len(coefficients_data) > 0:
                        elements.append(Paragraph(self._ensure_unicode("Коэффициенты:"), self.styles['CustomNormal']))
                    
                        # Создаем заголовки с переносом строк
                        headers = [
                            self._ensure_unicode("Переменная"),
                            self._ensure_unicode("Коэффициент"),
                            self._ensure_unicode("Стд.\nошибка"),
                            self._ensure_unicode("t-стат"),
                            self._ensure_unicode("P-Значение"),
                            self._ensure_unicode("Нижние\n95%"),
                            self._ensure_unicode("Верхние\n95%")
                        ]
                        
                        data = [headers]
                        for key, values in statistics["Коэффициенты"].items():
                            # Добавляем перенос строк для длинных названий переменных
                            if len(key) > 15:
                                # Разбиваем длинные названия на несколько строк
                                words = key.split()
                                if len(words) > 2:
                                    # Если больше 2 слов, разбиваем на строки по 2 слова
                                    wrapped_key = []
                                    for i in range(0, len(words), 2):
                                        wrapped_key.append(' '.join(words[i:i+2]))
                                    key = '\n'.join(wrapped_key)
                                elif len(key) > 25:
                                    # Если название очень длинное, разбиваем по символам
                                    # Ищем пробелы для разбиения
                                    if ' ' in key:
                                        parts = key.split(' ')
                                        # Разбиваем на части примерно по 15 символов
                                        wrapped_key = []
                                        current_line = ""
                                        for part in parts:
                                            if len(current_line + part) <= 15:
                                                current_line += (part + " ")
                                            else:
                                                if current_line:
                                                    wrapped_key.append(current_line.strip())
                                                current_line = part + " "
                                        if current_line:
                                            wrapped_key.append(current_line.strip())
                                        key = '\n'.join(wrapped_key)
                        
                            row = [self._ensure_unicode(key)]
                            for col in ["Коэффициент", "Стандартная ошибка", "t-статистика", "P-Значение", "Нижние 95%", "Верхние 95%"]:
                                value = values.get(col, "")
                                if isinstance(value, (int, float)):
                                    if col == "P-Значение":
                                        # Специальное форматирование для p-значений
                                        if value < 1e-10:
                                            value_str = "<1,0×10⁻¹⁰"
                                        elif value < 0.0001:
                                            value_str = "<0,0001"
                                        else:
                                            value_str = "{:.4f}".format(value).replace(".", ",")
                                    else:
                                        value_str = "{:.4f}".format(value).replace(".", ",")
                                else:
                                    value_str = "Н/Д"
                                row.append(self._ensure_unicode(value_str))
                            data.append(row)
                        
                        # Увеличиваем ширину колонок для лучшего отображения
                        # Автоматически определяем ширину колонок в зависимости от содержимого
                        total_width = 750  # Общая ширина для горизонтальной ориентации
                        
                        # Определяем ширину колонок на основе содержимого
                        col_widths = []
                        
                        # Первая колонка (Переменная) - шире для длинных названий
                        col_widths.append(200)
                        
                        # Остальные колонки - равномерно распределяем оставшееся место
                        remaining_width = total_width - 200
                        other_cols_width = remaining_width // 6  # 6 остальных колонок
                        
                        for i in range(6):
                            col_widths.append(other_cols_width)
                        
                        table = Table(data, colWidths=col_widths)
                        table.setStyle(TableStyle([
                            ('FONTNAME', (0, 0), (-1, -1), self.FONT_NAME),
                            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Уменьшаем размер шрифта
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('PADDING', (0, 0), (-1, -1), 8),  # Увеличиваем отступы
                            ('WORDWRAP', (0, 0), (-1, -1), True),  # Включаем перенос слов
                            ('LEFTPADDING', (0, 0), (-1, -1), 4),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                        ]))
                        elements.append(table)
                        elements.append(Spacer(1, 20))

            # 4. Интерпретация
            if has_interpretation:
                elements.append(Paragraph(self._ensure_unicode("Интерпретация результатов"), self.styles['CustomHeading']))
                
                for section, content in interpretation.items():
                    if section == 'error':
                        continue
                    
                    elements.append(Paragraph(self._ensure_unicode(section), self.styles['CustomNormal']))
                    
                    if isinstance(content, dict):
                        for subsection, text in content.items():
                            if text:
                                elements.append(Paragraph(self._ensure_unicode(f"{subsection}:"), self.styles['CustomNormal']))
                                elements.append(Paragraph(self._ensure_unicode(text), self.styles['CustomNormal']))
                    else:
                        if content:
                            elements.append(Paragraph(self._ensure_unicode(content), self.styles['CustomNormal']))
                    
                    elements.append(Spacer(1, 12))

            # 5. Графики (следуют друг за другом естественно)
            if has_figures:
                for i, figure in enumerate(figures):
                    img_path = self._figure_to_image(figure)
                    if img_path:
                        # Сначала график, потом заголовок
                        img = Image(img_path, width=500, height=350)
                        elements.append(img)
                        elements.append(Paragraph(self._ensure_unicode(f"График {i+1}"), self.styles['CustomHeading']))
                        elements.append(Spacer(1, 20))

            # В конце — если последний элемент PageBreak, удаляем его
            if elements and hasattr(elements[-1], '__class__') and 'PageBreak' in str(elements[-1].__class__):
                elements.pop()
            
            print("Создаем PDF...")
            try:
                # Финальная проверка: есть ли элементы для отображения
                if not elements:
                    print("ОШИБКА: Нет элементов для отображения в PDF!")
                    print("Проверьте, что предоставлены данные для отчета")
                    return False
                
                # Проверяем, что последний элемент не является PageBreak
                # (это может вызывать пустую страницу в конце)
                if elements and hasattr(elements[-1], '__class__') and 'PageBreak' in str(elements[-1].__class__):
                    print("Предупреждение: Последний элемент - PageBreak, удаляем его")
                    elements.pop()
                
                print(f"Количество элементов для добавления в PDF: {len(elements)}")
                
                # Создаем PDF
                doc.build(elements)
                print("Отчет успешно создан")
                
                # Удаляем временные файлы после успешного создания PDF
                self._cleanup_temp_files()
                
                return True
            except Exception as e:
                print(f"Ошибка при создании PDF: {str(e)}")
                # Удаляем временные файлы даже в случае ошибки
                self._cleanup_temp_files()
                raise
            
        except Exception as e:
            print(f"Ошибка при создании отчета: {str(e)}")
            print("Трассировка ошибки:")
            traceback.print_exc()
            # Удаляем временные файлы в случае ошибки
            self._cleanup_temp_files()
            return False