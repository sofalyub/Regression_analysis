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

class ReportGenerator:
    def __init__(self):
        # Регистрируем шрифты из папки fonts
        try:
            # Получаем абсолютный путь к текущему файлу
            current_dir = os.path.dirname(os.path.abspath(__file__))
            fonts_dir = os.path.join(current_dir, 'fonts')
            
            print(f"Текущая директория: {current_dir}")
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
            # Получаем figure из canvas
            figure = figure_canvas.figure
            
            # Устанавливаем более высокое разрешение для графика
            dpi = 150
            
            # Создаем временный файл
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            temp_file.close()
            
            # Сохраняем рисунок во временный файл
            figure.savefig(temp_file.name, format='png', dpi=dpi, bbox_inches='tight')
            
            # Добавляем файл в список для последующего удаления
            self.temp_files.append(temp_file.name)
            
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
            
            try:
                # Добавляем заголовок
                elements.append(Paragraph(self._ensure_unicode("Отчет по результатам"), self.styles['CustomTitle']))
                elements.append(Paragraph(self._ensure_unicode(f"Дата создания: {current_date}"), self.styles['CustomNormal']))
                elements.append(Spacer(1, 20))
                print("Заголовок добавлен")
            except Exception as e:
                print(f"Ошибка при добавлении заголовка: {str(e)}")
                raise
            
            try:
                # Добавляем уравнение
                elements.append(Paragraph(self._ensure_unicode("Уравнение регрессии:"), self.styles['CustomHeading']))
                elements.append(Paragraph(self._ensure_unicode(equation), self.styles['Equation']))
                elements.append(Spacer(1, 20))
                print("Уравнение добавлено")
            except Exception as e:
                print(f"Ошибка при добавлении уравнения: {str(e)}")
                raise
            
            # Добавляем статистику
            if statistics:
                print("Добавляем статистику...")
                try:
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
                        print("Регрессионная статистика добавлена")
                    
                    # Дисперсионный анализ
                    if "Дисперсионный анализ" in statistics:
                        elements.append(Paragraph(self._ensure_unicode("Дисперсионный анализ:"), self.styles['CustomNormal']))
                        data = [[self._ensure_unicode(col) for col in ["Источник", "df", "SS", "MS", "F", "Значимость F"]]]
                        for key in ["Регрессия", "Остаток", "Итого"]:
                            if key in statistics["Дисперсионный анализ"]:
                                row = [self._ensure_unicode(key)]
                                for col in ["df", "SS", "MS", "F", "Значимость F"]:
                                    value = statistics["Дисперсионный анализ"][key].get(col, "")
                                    if isinstance(value, (int, float)):
                                        if col == "df":
                                            value_str = str(int(value))
                                        elif col in ["F", "Значимость F"]:
                                            value_str = "{:.4f}".format(value).replace(".", ",")
                                        else:
                                            value_str = "{:.2f}".format(value).replace(".", ",")
                                    else:
                                        value_str = ""
                                    row.append(self._ensure_unicode(value_str))
                                data.append(row)
                        
                        table = Table(data, colWidths=[150, 80, 120, 120, 120, 120])
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
                        print("Дисперсионный анализ добавлен")
                    
                    # Коэффициенты
                    if "Коэффициенты" in statistics:
                        elements.append(Paragraph(self._ensure_unicode("Коэффициенты:"), self.styles['CustomNormal']))
                        data = [[self._ensure_unicode(col) for col in ["Переменная", "Коэффициент", "Стд. ошибка", "t-стат", "P-Значение", "Нижние 95%", "Верхние 95%"]]]
                        for key, values in statistics["Коэффициенты"].items():
                            row = [self._ensure_unicode(key)]
                            for col in ["Коэффициент", "Стандартная ошибка", "t-статистика", "P-Значение", "Нижние 95%", "Верхние 95%"]:
                                value = values.get(col, "")
                                if isinstance(value, (int, float)):
                                    value_str = "{:.4f}".format(value).replace(".", ",")
                                else:
                                    value_str = "Н/Д"
                                row.append(self._ensure_unicode(value_str))
                            data.append(row)
                        
                        table = Table(data, colWidths=[120, 100, 100, 100, 100, 100, 100])
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
                        print("Коэффициенты добавлены")
                except Exception as e:
                    print(f"Ошибка при добавлении статистики: {str(e)}")
                    raise
            
            # Добавляем интерпретацию
            if interpretation:
                print("Добавляем интерпретацию...")
                try:
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
                    print("Интерпретация добавлена")
                except Exception as e:
                    print(f"Ошибка при добавлении интерпретации: {str(e)}")
                    raise
            
            # Добавляем графики
            if figures:
                print("Добавляем графики...")
                try:
                    for i, figure in enumerate(figures):
                        # Добавляем разрыв страницы перед каждым графиком
                        elements.append(PageBreak())
                        elements.append(Paragraph(self._ensure_unicode(f"График {i+1}"), self.styles['CustomHeading']))
                        # Конвертируем matplotlib figure в изображение
                        img_path = self._figure_to_image(figure)
                        if img_path:
                            # Создаем объект Image из файла с уменьшенным размером
                            img = Image(img_path, width=600, height=400)
                            elements.append(img)
                            elements.append(Spacer(1, 20))
                    print("Графики добавлены")
                except Exception as e:
                    print(f"Ошибка при добавлении графиков: {str(e)}")
                    raise
            
            print("Создаем PDF...")
            try:
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