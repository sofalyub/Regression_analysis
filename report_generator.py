"""
Модуль для генерации отчетов с результатами регрессионного анализа
"""

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QDateTime, Qt
from reportlab.lib.pagesizes import A4, landscape  # Добавляем landscape для альбомной ориентации
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

# Путь к директории с шрифтами
fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')

# Регистрация шрифтов с поддержкой кириллицы
try:
    # Пытаемся зарегистрировать DejaVuSans (обычно имеет хорошую поддержку кириллицы)
    dejavu_path = os.path.join(fonts_dir, 'DejaVuSans.ttf')
    dejavu_bold_path = os.path.join(fonts_dir, 'DejaVuSans-Bold.ttf')
    
    pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', dejavu_bold_path))
    FONT_NAME = 'DejaVuSans'
except Exception as e:
    print(f"Не удалось зарегистрировать шрифт DejaVuSans: {e}")
    # Если DejaVuSans недоступен, используем стандартный Helvetica
    FONT_NAME = 'Helvetica'


class ReportGenerator:
    """
    Класс для генерации отчетов по результатам регрессионного анализа
    """
    
    def __init__(self):
        """
        Инициализация генератора отчетов
        """
        self.styles = getSampleStyleSheet()
        # Создаем стиль для заголовков с поддержкой кириллицы
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontName=f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.darkblue,
            encoding='utf-8'
        ))
        
        # Создаем стиль для подзаголовков
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontName=f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.navy,
            encoding='utf-8'
        ))
        
        # Создаем стиль для обычного текста
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontName=FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica',
            fontSize=11,
            leading=14,
            encoding='utf-8'
        ))
        
        # Создаем стиль для уравнения регрессии
        self.styles.add(ParagraphStyle(
            name='Equation',
            parent=self.styles['Normal'],
            fontName=FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica',
            fontSize=12,
            leading=16,
            alignment=1,  # По центру
            spaceAfter=10,
            encoding='utf-8'
        ))
    
    def generate_report(self, parent_widget, equation, statistics, interpretation, figures, model_type="Линейная регрессия"):
        """
        Создание и сохранение отчета в формате PDF
        
        Args:
            parent_widget: Родительский виджет для диалога сохранения
            equation (str): Уравнение регрессии
            statistics (dict): Статистика регрессии
            interpretation (dict): Интерпретация результатов
            figures (list): Список графиков для включения в отчет
            model_type (str): Тип модели регрессии
        
        Returns:
            bool: True, если отчет успешно создан и сохранен, иначе False
        """
        try:
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
                return False  # Пользователь отменил операцию
            
            # Если пользователь не указал расширение .pdf, добавляем его
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # Создаем документ PDF в альбомной ориентации
            doc = SimpleDocTemplate(file_path, 
                                   pagesize=landscape(A4),  # Используем альбомную ориентацию
                                   rightMargin=36, leftMargin=36,  # Уменьшаем отступы
                                   topMargin=72, bottomMargin=36)
            
            # Контейнер для хранения элементов документа
            elements = []
            
            # Добавляем заголовок отчета
            title = Paragraph(f"Отчет по результатам", self.styles['CustomTitle'])
            elements.append(title)
            elements.append(Spacer(1, 0.25*inch))
            
            # Добавляем дату создания отчета
            date_text = Paragraph(f"Дата создания: {current_date}", self.styles['CustomNormal'])
            elements.append(date_text)
            elements.append(Spacer(1, 0.25*inch))
            
            # Добавляем уравнение регрессии
            elements.append(Paragraph("Уравнение регрессии:", self.styles['CustomHeading']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Форматируем уравнение для лучшего отображения
            formatted_equation = equation.replace(" + ", " + ").replace(" - ", " - ")
            equation_para = Paragraph(formatted_equation, self.styles['Equation'])
            elements.append(equation_para)
            elements.append(Spacer(1, 0.25*inch))
            
            # Добавляем статистику регрессии
            elements.append(Paragraph("Статистика регрессии:", self.styles['CustomHeading']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Добавляем регрессионную статистику
            if "Регрессионная статистика" in statistics:
                reg_stats = statistics["Регрессионная статистика"]
                # Создаем таблицу с регрессионной статистикой с автоматическим определением ширины
                reg_stats_data = []
                reg_stats_data.append(["Показатель", "Значение"])
                
                for key, value in reg_stats.items():
                    # Форматируем числовые значения
                    if isinstance(value, (int, float)):
                        if key == "Наблюдения":
                            value_str = str(int(value))
                        else:
                            value_str = "{:.4f}".format(value).replace(".", ",")
                    else:
                        value_str = "Н/Д"
                    
                    reg_stats_data.append([key, value_str])
                
                # Создаем и стилизуем таблицу с заданными ширинами столбцов
                reg_stats_table = Table(reg_stats_data, colWidths=[3.0*inch, 1.5*inch])
                reg_stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                    ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (1, 0), f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (1, -1), FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (1, 0), 6),
                    ('BACKGROUND', (0, 1), (1, -1), colors.white),
                    ('GRID', (0, 0), (1, -1), 1, colors.grey),
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
                    # Добавляем отступы внутри ячеек для лучшей читаемости
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    # ДОБАВЛЕНИЕ: Включаем перенос текста для всех ячеек
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    # Вертикальное выравнивание по центру
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(reg_stats_table)
                elements.append(Spacer(1, 0.2*inch))
            
            # Добавляем дисперсионный анализ
            if "Дисперсионный анализ" in statistics:
                elements.append(Paragraph("Дисперсионный анализ:", self.styles['CustomHeading']))
                elements.append(Spacer(1, 0.1*inch))
                
                disp_stats = statistics["Дисперсионный анализ"]
                # Создаем и стилизуем таблицу с данными дисперсионного анализа с измененными заголовками
                disp_data = []
                disp_data.append(["", "df", "SS", "MS", "F", "Знач. F"])
                
                for key in ["Регрессия", "Остаток", "Итого"]:
                    if key in disp_stats:
                        row = [key]
                        for col in ["df", "SS", "MS", "F", "Значимость F"]:
                            value = disp_stats[key].get(col, "")
                            if isinstance(value, (int, float)):
                                if col == "df":
                                    value_str = str(int(value))
                                elif col in ["F", "Значимость F"]:
                                    value_str = "{:.4f}".format(value).replace(".", ",")
                                else:
                                    value_str = "{:.2f}".format(value).replace(".", ",")
                            else:
                                value_str = ""
                            row.append(value_str)
                        disp_data.append(row)
                
                # Создаем и стилизуем таблицу с заданными ширинами столбцов
                disp_table = Table(disp_data, colWidths=[1.3*inch, 0.7*inch, 1.8*inch, 1.8*inch, 0.8*inch, 0.8*inch])
                disp_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    # Добавляем отступы внутри ячеек
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    # ДОБАВЛЕНИЕ: Включаем перенос текста для всех ячеек
                    ('WORDWRAP', (0, 0), (-1, -1), True),
                    # Вертикальное выравнивание по центру
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                elements.append(disp_table)
                elements.append(Spacer(1, 0.2*inch))
            
            # Добавляем таблицу коэффициентов
            if "Коэффициенты" in statistics:
                elements.append(Paragraph("Коэффициенты:", self.styles['CustomHeading']))
                elements.append(Spacer(1, 0.1*inch))
                
                coef_stats = statistics["Коэффициенты"]
                # Создаем данные для таблицы коэффициентов с сокращенными заголовками
                coef_data = []
                # ИЗМЕНЕНИЕ: Увеличиваем ширину заголовков для лучшей читаемости
                coef_data.append(["", "Коэф.", "Ст.ошибка", "t-стат.", "P-знач.", "Нижн.95%", "Верх.95%"])
                
                # Функция для форматирования длинных текстов
                def format_long_text(text, max_length=25):
                    """
                    Разбивает длинный текст на несколько строк для лучшего отображения в таблице
                    """
                    if len(str(text)) <= max_length:
                        return str(text)
                    
                    words = str(text).split()
                    lines = []
                    current_line = ""
                    
                    for word in words:
                        if len(current_line) + len(word) + 1 <= max_length:
                            if current_line:
                                current_line += " " + word
                            else:
                                current_line = word
                        else:
                            lines.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines.append(current_line)
                    
                    return "\n".join(lines)
                
                for key, values in coef_stats.items():
                    # Форматируем длинные названия переменных
                    formatted_key = format_long_text(key)
                    
                    row = [formatted_key]
                    for col in ["Коэффициент", "Стандартная ошибка", "t-статистика", "P-Значение", "Нижние 95%", "Верхние 95%"]:
                        value = values.get(col, "")
                        if isinstance(value, (int, float)):
                            value_str = "{:.4f}".format(value).replace(".", ",")
                        else:
                            value_str = "Н/Д"
                        row.append(value_str)
                    coef_data.append(row)
                
                # Создаем и стилизуем таблицу с увеличенной шириной первого столбца
                if len(coef_data) > 8:
                    # Для первой таблицы с заголовком
                    # ИЗМЕНЕНИЕ: Используем None для автоматического определения ширины столбцов по содержимому
                    coef_table1 = Table(coef_data[:8])
                    coef_table1.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                        # Добавляем отступы внутри ячеек
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    elements.append(coef_table1)
                    elements.append(Spacer(1, 0.2*inch))
                    
                    # Добавляем новую страницу если много коэффициентов
                    if len(coef_data) > 15:
                        elements.append(PageBreak())
                        elements.append(Paragraph("Коэффициенты (продолжение):", self.styles['CustomHeading']))
                        elements.append(Spacer(1, 0.1*inch))
                    
                    # Для второй таблицы с остальными коэффициентами
                    coef_data_rest = [coef_data[0]] + coef_data[8:]  # Заголовок + оставшиеся строки
                    # ИЗМЕНЕНИЕ: Задаем ширину для всех столбцов, чтобы обеспечить правильное отображение
                    coef_table2 = Table(coef_data_rest, colWidths=[2.5*inch, 1.1*inch, 1.1*inch, 0.9*inch, 0.9*inch, 1.3*inch, 1.3*inch])
                    coef_table2.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),  # Добавляем отступ сверху
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Выравниваем текст в первой колонке по левому краю
                        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                        # Добавляем отступы внутри ячеек
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        # Включаем перенос текста для всех ячеек
                        ('WORDWRAP', (0, 0), (-1, -1), True),
                        # Вертикальное выравнивание по центру
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    
                    elements.append(coef_table2)
                else:
                    # Если мало коэффициентов, создаем одну таблицу
                    # ИЗМЕНЕНИЕ: Задаем ширину для всех столбцов, чтобы обеспечить правильное отображение
                    coef_table = Table(coef_data, colWidths=[2.5*inch, 1.1*inch, 1.1*inch, 0.9*inch, 0.9*inch, 1.3*inch, 1.3*inch])
                    coef_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), f'{FONT_NAME}-Bold' if FONT_NAME != 'Helvetica' else 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME if FONT_NAME != 'Helvetica' else 'Helvetica'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),  # Добавляем отступ сверху
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ALIGN', (0, 0), (0, -1), 'LEFT'),   # Выравниваем текст в первой колонке по левому краю
                        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                        # Добавляем отступы внутри ячеек
                        ('LEFTPADDING', (0, 0), (-1, -1), 12),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                        # Включаем перенос текста для всех ячеек
                        ('WORDWRAP', (0, 0), (-1, -1), True),
                        # Вертикальное выравнивание по центру
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    
                    elements.append(coef_table)
                
                elements.append(Spacer(1, 0.2*inch))
            
            # Добавляем новую страницу перед интерпретацией
            elements.append(PageBreak())
            
            # Добавляем интерпретацию результатов
            elements.append(Paragraph("Интерпретация результатов:", self.styles['CustomHeading']))
            elements.append(Spacer(1, 0.1*inch))
            
            for section, content in interpretation.items():
                if section == 'error':
                    continue  # Пропускаем сообщения об ошибках
                
                elements.append(Paragraph(section, self.styles['CustomHeading']))
                elements.append(Spacer(1, 0.05*inch))
                
                if isinstance(content, dict):
                    for subsection, text in content.items():
                        if text:  # Проверяем, что текст не пустой
                            elements.append(Paragraph(f"<b>{subsection}:</b>", self.styles['CustomNormal']))
                            elements.append(Paragraph(text, self.styles['CustomNormal']))
                            elements.append(Spacer(1, 0.1*inch))
                else:
                    if content:  # Проверяем, что текст не пустой
                        elements.append(Paragraph(content, self.styles['CustomNormal']))
                        elements.append(Spacer(1, 0.1*inch))
            
            # Добавляем графики, создавая новую страницу для каждого
            if figures:
                for i, figure in enumerate(figures):
                    # Добавляем новую страницу для каждого графика
                    elements.append(PageBreak())
                    elements.append(Paragraph(f"График {i+1}:", self.styles['CustomHeading']))
                    elements.append(Spacer(1, 0.1*inch))
                    
                    # Конвертируем matplotlib figure в изображение
                    img_data = self._figure_to_image(figure)
                    if img_data:
                        # Создаем изображение и указываем ширину (сохраняя пропорции)
                        # ИЗМЕНЕНИЕ: Увеличиваем размер графика для лучшей визуализации
                        img = Image(img_data, width=7.5*inch, height=5.5*inch)
                        # Добавляем изображение в отчет
                        elements.append(img)
            
            # Создаем PDF-документ
            doc.build(elements)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при создании отчета: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _figure_to_image(self, figure_canvas):
        """
        Преобразует matplotlib figure в изображение для PDF
        
        Args:
            figure_canvas: FigureCanvas из matplotlib
        
        Returns:
            BytesIO: Объект с данными изображения или None в случае ошибки
        """
        try:
            # Получаем figure из canvas
            figure = figure_canvas.figure
            
            # ИЗМЕНЕНИЕ: Устанавливаем более высокое разрешение для графика
            dpi = 150  # Увеличиваем DPI с 100 до 150
            
            # Создаем буфер для сохранения изображения
            img_data = BytesIO()
            
            # Сохраняем рисунок в буфер с увеличенным разрешением и плотным размещением
            figure.savefig(img_data, format='png', dpi=dpi, bbox_inches='tight')
            img_data.seek(0)  # Перемещаемся в начало буфера
            
            return img_data
        
        except Exception as e:
            print(f"Ошибка при конвертации графика: {str(e)}")
            import traceback
            traceback.print_exc()
            return None