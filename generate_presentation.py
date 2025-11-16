#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для генерации PDF презентации проекта.
Использует reportlab для создания презентации.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os

# Попытка использовать шрифт с поддержкой кириллицы
FONT_NAME = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'

# Попытка зарегистрировать шрифт с поддержкой кириллицы на Windows
if os.name == 'nt':
    try:
        # Стандартные пути к шрифтам Windows (пробуем несколько вариантов)
        font_candidates = [
            ('Arial', 'C:/Windows/Fonts/arial.ttf', ['C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/ARIALBD.TTF']),
            ('TimesNewRoman', 'C:/Windows/Fonts/times.ttf', ['C:/Windows/Fonts/timesbd.ttf', 'C:/Windows/Fonts/TIMESBD.TTF']),
        ]
        
        for font_name, regular_path, bold_paths in font_candidates:
            if os.path.exists(regular_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, regular_path))
                    FONT_NAME = font_name
                    # Пробуем найти bold версию
                    for bold_path in bold_paths:
                        if os.path.exists(bold_path):
                            try:
                                pdfmetrics.registerFont(TTFont(f'{font_name}Bold', bold_path))
                                FONT_BOLD = f'{font_name}Bold'
                                break
                            except Exception:
                                continue
                    break
                except Exception:
                    continue
    except Exception:
        pass  # Используем Helvetica по умолчанию

def create_presentation(output_file='presentation.pdf'):
    """Создает PDF презентацию проекта."""
    
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Кастомные стили
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=FONT_BOLD
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=20,
        spaceBefore=20,
        fontName=FONT_BOLD
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        fontName=FONT_BOLD
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName=FONT_NAME
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        leftIndent=20,
        fontName=FONT_NAME
    )
    
    # Слайд 1: Титульный
    story.append(Paragraph("Автоматизация препродакшн-подготовки сценариев", title_style))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Команда DiverCity", heading_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Сервис для автоматического создания препродакшн-таблиц из сценариев", body_style))
    story.append(PageBreak())
    
    # Слайд 2: Проблема
    story.append(Paragraph("Проблема", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    problems = [
        "Подготовка препродакшн-документации занимает многочасовые монотонные правки",
        "Ручное определение локаций, времени суток, персонажей, массовки, реквизита",
        "Ошибки приводят к сбоям в графике и дополнительным затратам на площадке",
        "Отсутствие автоматического распознавания производственных элементов",
        "Неоднозначные формулировки и опечатки в сценариях"
    ]
    
    for problem in problems:
        story.append(Paragraph(f"• {problem}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 3: Решение
    story.append(Paragraph("Решение", heading_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Автоматический сервис, который загружает сценарий в формате PDF или DOCX "
        "и генерирует готовую препродакшн-таблицу со всеми производственными элементами.",
        body_style
    ))
    story.append(Spacer(1, 0.5*cm))
    
    solution_points = [
        "Автоматическое распознавание номеров сцен и сегментация текста",
        "Извлечение локаций, времени суток, персонажей, массовки, реквизита",
        "Определение спецэффектов, трюков, транспорта, животных",
        "Генерация структурированной таблицы с настраиваемыми столбцами",
        "Экспорт в CSV и XLSX с сохранением кодировок"
    ]
    
    for point in solution_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 4: Архитектура
    story.append(Paragraph("Архитектура решения", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    architecture_data = [
        ['Компонент', 'Технология', 'Назначение'],
        ['Frontend', 'Streamlit', 'Веб-интерфейс для загрузки файлов и просмотра результатов'],
        ['Backend', 'FastAPI', 'REST API для обработки запросов'],
        ['Парсер', 'PyMuPDF, python-docx', 'Извлечение текста из PDF и DOCX'],
        ['Сегментатор', 'Regex, Python', 'Распознавание номеров сцен и разбиение на сцены'],
        ['Экстрактор', 'Ключевые слова, правила', 'Извлечение производственных элементов'],
        ['Генератор', 'Pandas', 'Формирование таблиц и экспорт']
    ]
    
    arch_table = Table(architecture_data, colWidths=[3*cm, 3*cm, 9*cm])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(arch_table)
    story.append(PageBreak())
    
    # Слайд 5: Функциональность - Сегментация
    story.append(Paragraph("Корректная сегментация сценария", heading_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Система автоматически распознает номера сцен в различных форматах:",
        body_style
    ))
    story.append(Spacer(1, 0.3*cm))
    
    segmentation_points = [
        "Поддержка различных форматов: 'СЦЕНА 11', '11-N2', '1-11N2', '15-N6-04', '3/П'",
        "Автоматическое разбиение текста на отдельные сцены",
        "Корректная обработка документов в форматах PDF и DOCX",
        "Поддержка различных кодировок (UTF-8, UTF-16, CP1251, KOI8-R и др.)",
        "Обработка сценариев объемом до 120 страниц"
    ]
    
    for point in segmentation_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 6: Функциональность - Извлечение элементов
    story.append(Paragraph("Извлечение ключевых элементов", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    extraction_data = [
        ['Элемент', 'Примеры'],
        ['Локации', 'Объект: "кабинет", "улица", "корабль"<br/>Подобъект: "кают-компания", "палуба"'],
        ['Время суток', 'День, ночь, утро, вечер'],
        ['Персонажи', 'Основные и второстепенные персонажи'],
        ['Массовка', 'Толпа, официанты, прохожие'],
        ['Реквизит', 'Автомобиль, оружие, документы'],
        ['Транспорт', 'Игровой транспорт в сцене'],
        ['Трюки', 'Каскадеры, пиротехника'],
        ['Животные', 'Животные в сцене'],
        ['Спецэффекты', 'Визуальные и звуковые эффекты']
    ]
    
    ext_table = Table(extraction_data, colWidths=[4*cm, 11*cm])
    ext_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(ext_table)
    story.append(PageBreak())
    
    # Слайд 7: Пользовательский интерфейс - Загрузка
    story.append(Paragraph("Удобство загрузки и просмотра", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    ui_points = [
        "Интуитивная загрузка нескольких файлов одновременно (PDF и DOCX)",
        "Выбор пресета таблицы: базовый, расширенный или полный анализ",
        "Возможность настройки кастомных столбцов",
        "Наглядное представление результатов в виде интерактивной таблицы",
        "Прогресс-бар и отображение промежуточных этапов обработки",
        "Быстрое первичное отображение результатов",
        "Время обработки среднего сценария не превышает 5 минут"
    ]
    
    for point in ui_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 8: Пользовательский интерфейс - Работа с данными
    story.append(Paragraph("Работа с данными и экспорт", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    data_work_points = [
        "Редактирование ячеек прямо в интерфейсе с моментальным сохранением",
        "Фильтрация по столбцам для быстрого поиска нужных сцен",
        "Поиск по содержимому таблицы",
        "Экспорт в CSV с кодировкой UTF-8-BOM для корректного отображения в Excel",
        "Экспорт в XLSX с сохранением структуры и форматирования",
        "Поддержка работы с несколькими сериями в одной таблице"
    ]
    
    for point in data_work_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 9: Практическая применимость
    story.append(Paragraph("Практическая применимость", heading_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Решение полностью соответствует реальным потребностям производственных команд:",
        body_style
    ))
    story.append(Spacer(1, 0.3*cm))
    
    applicability_points = [
        "Все необходимые элементы для препродакшн-планирования присутствуют в таблице",
        "Результаты готовы к использованию без дополнительной ручной обработки",
        "Соответствие формату препродакшн-таблиц, используемых в индустрии",
        "Поддержка работы с несколькими сериями одновременно",
        "Автоматическое извлечение номера серии из имени файла",
        "Гибкая настройка структуры таблицы под специфику проекта"
    ]
    
    for point in applicability_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 10: Точность и полнота
    story.append(Paragraph("Точность и полнота извлечения", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    accuracy_points = [
        "Использование комбинации правил и ключевых слов для извлечения элементов",
        "Обработка неоднозначных формулировок и опечаток в исходном сценарии",
        "Корректное соответствие элементов к сценам",
        "Полнота распознавания всех ключевых элементов",
        "Отсутствие пропусков в определении локаций, персонажей и реквизита",
        "Возможность ручной корректировки результатов в интерфейсе"
    ]
    
    for point in accuracy_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 11: Технические характеристики
    story.append(Paragraph("Технические характеристики", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    tech_data = [
        ['Параметр', 'Значение'],
        ['Форматы входных файлов', 'PDF, DOCX'],
        ['Объем обработки', 'До 120 страниц'],
        ['Время обработки', 'До 5 минут для среднего сценария'],
        ['Поддерживаемые кодировки', 'UTF-8, UTF-16, CP1251, KOI8-R, ISO-8859-5, MacRoman, ASCII'],
        ['Форматы экспорта', 'CSV (UTF-8-BOM), XLSX'],
        ['Работа без внешних API', 'Все модели локальные'],
        ['Развертывание', 'Docker, локальная установка']
    ]
    
    tech_table = Table(tech_data, colWidths=[6*cm, 9*cm])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    story.append(tech_table)
    story.append(PageBreak())
    
    # Слайд 12: Преимущества решения
    story.append(Paragraph("Преимущества решения", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    advantages_points = [
        "Экономия времени: автоматизация многочасовой ручной работы",
        "Снижение ошибок: исключение человеческого фактора при обработке",
        "Стандартизация: единый формат препродакшн-таблиц",
        "Масштабируемость: обработка нескольких серий одновременно",
        "Гибкость: настройка структуры таблицы под проект",
        "Удобство: интуитивный интерфейс без необходимости обучения"
    ]
    
    for point in advantages_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 13: Пример выходной таблицы
    story.append(Paragraph("Структура выходной таблицы", heading_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Таблица содержит следующие столбцы (в зависимости от выбранного пресета):",
        body_style
    ))
    story.append(Spacer(1, 0.3*cm))
    
    columns = [
        "Серия", "Сцена", "Режим", "Инт / нат", "Объект", "Подобъект",
        "Синопсис", "Время года", "Персонажи", "Массовка", "Грим",
        "Костюм", "Реквизит", "Игровой транспорт", "Трюк", "Животные"
    ]
    
    # Разбиваем на две колонки для компактности
    col_text = ", ".join(columns[:8]) + ",\n" + ", ".join(columns[8:])
    story.append(Paragraph(col_text, body_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Каждая строка соответствует отдельной сцене со всеми извлеченными элементами.",
        body_style
    ))
    
    story.append(PageBreak())
    
    # Слайд 14: Планы развития
    story.append(Paragraph("Планы развития", heading_style))
    story.append(Spacer(1, 0.5*cm))
    
    future_points = [
        "Дообучение моделей машинного обучения на GPU для повышения точности",
        "Улучшение извлечения грима, костюмов и трюков с учетом контекста",
        "Интеграция с системами планирования съемок",
        "Расширение словарей и правил для различных жанров",
        "Автоматическое определение времени года по контексту",
        "Улучшение обработки сложных сцен с множеством элементов"
    ]
    
    for point in future_points:
        story.append(Paragraph(f"• {point}", bullet_style))
    
    story.append(PageBreak())
    
    # Слайд 15: Заключение
    story.append(Paragraph("Заключение", heading_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Решение полностью автоматизирует процесс создания препродакшн-таблиц, "
        "значительно сокращая время подготовки и снижая количество ошибок.",
        body_style
    ))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Сервис готов к использованию в реальных проектах и может быть легко "
        "развернут с помощью Docker или локальной установки.",
        body_style
    ))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Спасибо за внимание!", title_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Команда DiverCity", heading_style))
    
    # Генерация PDF
    doc.build(story)
    print(f"Presentation successfully created: {output_file}")

if __name__ == '__main__':
    create_presentation('presentation.pdf')

