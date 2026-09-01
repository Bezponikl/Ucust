"""
generate_audit_pdf.py
======================================================================
Генерация официального PDF-отчета:
"UCust.AI — Аудит готовности архитектуры и Дорожная карта (Roadmap)"
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class NumberedCanvas(canvas.Canvas):
    """Нумератор страниц и колонтитулы."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Arial", 8)
        self.setFillColor(colors.HexColor("#6B7280"))
        
        # Верхний колонтитул
        self.drawString(1.5 * cm, A4[1] - 1.2 * cm, "UCust.AI — Архитектурный аудит и статус готовности системы")
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.5)
        self.line(1.5 * cm, A4[1] - 1.3 * cm, A4[0] - 1.5 * cm, A4[1] - 1.3 * cm)

        # Нижний колонтитул
        self.line(1.5 * cm, 1.3 * cm, A4[0] - 1.5 * cm, 1.3 * cm)
        self.drawString(1.5 * cm, 0.9 * cm, "Конфиденциально • Разработано для UCust Enterprise")
        page_text = f"Страница {self._pageNumber} из {page_count}"
        self.drawRightString(A4[0] - 1.5 * cm, 0.9 * cm, page_text)
        self.restoreState()


def build_pdf():
    # Регистрация кириллических шрифтов Windows
    font_path = "C:/Windows/Fonts/arial.ttf"
    font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    pdfmetrics.registerFont(TTFont("Arial", font_path))
    pdfmetrics.registerFont(TTFont("Arial-Bold", font_bold_path))

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    pdf_filename = os.path.join(output_dir, "UCust_AI_Readiness_Audit_and_Roadmap.pdf")

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm
    )

    styles = getSampleStyleSheet()
    
    # Кастомные стили
    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=6
    )
    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=14
    )
    style_h1 = ParagraphStyle(
        "H1",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=12,
        spaceAfter=8
    )
    style_h2 = ParagraphStyle(
        "H2",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2563EB"),
        spaceBefore=8,
        spaceAfter=4
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4
    )
    style_cell = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1F2937")
    )
    style_cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1F2937")
    )
    style_badge_ready = ParagraphStyle(
        "BadgeReady",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#065F46"),
        alignment=1
    )
    style_badge_partial = ParagraphStyle(
        "BadgePartial",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#92400E"),
        alignment=1
    )

    story = []

    # Заголовок
    story.append(Paragraph("UCust.AI — Аудит готовности архитектуры", style_title))
    story.append(Paragraph("Комплексный отчет соответствия спецификации и дорожная карта (Roadmap)", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=12))

    # Раздел 1: Сводная таблица
    story.append(Paragraph("1. Сводная таблица готовности по 11 разделам спецификации", style_h1))
    
    table_data = [
        [
            Paragraph("№", style_cell_bold),
            Paragraph("Раздел спецификации", style_cell_bold),
            Paragraph("Статус", style_cell_bold),
            Paragraph("Ключевые модули и реализация в коде", style_cell_bold)
        ],
        [
            Paragraph("1", style_cell_bold),
            Paragraph("Общая концепция (Digital Business Model)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("UnifiedOrchestrator, UserProfile в SQL + 7 семантических категорий Clean RAG.", style_cell)
        ],
        [
            Paragraph("2", style_cell_bold),
            Paragraph("Источники данных (Сайт, Соцсети, Карты)", style_cell),
            Paragraph("🟨 85%", style_badge_partial),
            Paragraph("Сайт (WebsiteCollector), TG (TelethonCollector), VK (VKCollector). Карты — базовый каркас.", style_cell)
        ],
        [
            Paragraph("3", style_cell_bold),
            Paragraph("Сбор данных с сайта (Website Crawling)", style_cell),
            Paragraph("🟨 90%", style_badge_partial),
            Paragraph("Рекурсивный обход подстраниц, фильтрация лого/шапок, отбор товаров, H1-H3, цены, контакты.", style_cell)
        ],
        [
            Paragraph("4", style_cell_bold),
            Paragraph("Сбор из соцсетей (Social Extraction)", style_cell),
            Paragraph("🟨 85%", style_badge_partial),
            Paragraph("Telegram и VK нативно. Сбор постов, ER, лайков, комментариев. Instagram/TikTok — через proxy.", style_cell)
        ],
        [
            Paragraph("5", style_cell_bold),
            Paragraph("Сбор с карт и агрегаторов (Maps & Reviews)", style_cell),
            Paragraph("🟨 70%", style_badge_partial),
            Paragraph("YandexMapsCollector, TwoGISCollector — парсинг структуры отзывов, рейтинга и адреса.", style_cell)
        ],
        [
            Paragraph("6", style_cell_bold),
            Paragraph("Агрегация данных (Data Fusion)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("Синтез досье сайта, профиля, фотосеток, инфоповодов и отзывов в единый цифровой профиль.", style_cell)
        ],
        [
            Paragraph("7", style_cell_bold),
            Paragraph("Аналитический блок (Audience, Pains, SWOT)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("ContentStrategyEngine, SaigaLLM — сегментация ЦА, извлечение болей/триггеров, SWOT.", style_cell)
        ],
        [
            Paragraph("8", style_cell_bold),
            Paragraph("Формирование стратегии (Strategy Engine)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("Воронка TOFU/MOFU/BOFU, визуальная сетка 3x3, арсенал хуков, календарь праздников.", style_cell)
        ],
        [
            Paragraph("9", style_cell_bold),
            Paragraph("Генерация контента (Content Generation)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("SaigaLLMSkill + CriticMunger (Self-Healing Loop), ComfyUI FLUX/SDXL, LTX-Video.", style_cell)
        ],
        [
            Paragraph("10", style_cell_bold),
            Paragraph("Публикация (Execution)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("Broadcaster, api_gateway — отложенная публикация в Telegram, VK, MAX; трекинг в SQL.", style_cell)
        ],
        [
            Paragraph("11", style_cell_bold),
            Paragraph("Анализ обратной связи (Feedback Loop)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("FeedbackLoopEngine — расчет ER, тональность, FAQ/возражения, RAG, адаптация контент-плана.", style_cell)
        ]
    ]

    col_widths = [0.8 * cm, 4.8 * cm, 2.0 * cm, 10.4 * cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))

    # Раздел 2: Детальный разбор готовых компонентов
    story.append(Paragraph("2. Реализованный функционал (Готово на 100%)", style_h1))
    
    ready_points = [
        ("Автономная цифровая модель бизнеса (SQL + Clean RAG):",
         "Система принимает URL сайта и автоматически формирует 7 категорий знаний: Бренд и УТП, Боли и триггеры, Конкуренты, Визуальный брендбук 3x3, Досье сайта, История фото-промптов, Календарь праздников и событий."),
        
        ("Умный сбор сайта и фильтрация изображений (WebsiteCollector):",
         "Автоматический обход страниц (О нас, Услуги, Блог, Контакты), извлечение цен и УТП. Внедрен алгоритм отсева мусора: блокируются логотипы, шапки, иконки соцсетей, берутся только качественные фото товаров и портфолио (>180x180 px)."),
        
        ("Визуальный брендбук и сетка 3x3 (AdvancedVisualDirector):",
         "Определение доминирующего цвета, расчет палитры Hex, разметка 9 слотов сетки ленты (детали, портрет, процесс, продукт) для гармоничного визуала."),
        
        ("Модуль праздников и инфоповодов (EventHolidayCollector):",
         "Календарь государственных праздников (Россия, Беларусь, Казахстан, Узбекистан, СНГ), 50+ дней городов и профессиональных дат (IT, медицина, автосервис, бьюти, рестораны, стройка). Автоматическое внедрение праздничных постов в 30-дневный план."),
        
        ("Замкнутый цикл аналитики и самообучение (FeedbackLoopEngine):",
         "Сбор комментариев и расчет вовлеченности (ER). Семантическое извлечение частых вопросов клиентов (FAQ) и ключевых возражений («дорого», «гарантия»). Автоматическая генерация постов-ответов в новом контент-плане."),
        
        ("Мульти-генерация и безопасность (SaigaLLM + ComfyUI + Critic):",
         "Генерация текстов в строгом White-Label режиме (без утечки внутренних параметров), многоступенчатая проверка критиком (CriticMunger) с автоматическим самоисправлением (Self-Healing Loop), создание фото через FLUX/SDXL и видео через LTX-Video."),
        
        ("Управление медиа-файлами (MediaRetentionManager):",
         "Очистка временного кэша парсинга каждые 5 часов, долгосрочная архивация сгенерированных фото/видео через 30 дней.")
    ]

    for title, desc in ready_points:
        story.append(Paragraph(f"• <b>{title}</b> {desc}", style_body))

    story.append(Spacer(1, 10))

    # Раздел 3: Недостающие элементы и Дорожная карта
    story.append(Paragraph("3. Недостающие элементы и Дорожная карта (Roadmap до 100%)", style_h1))
    
    missing_points = [
        ("1. Модуль разбора клиентских документов (DocumentCollector)",
         "<b>Что требуется:</b> Поддержка загрузки и извлечения текста/таблиц из файлов PDF (презентации, коммерческие предложения), DOCX (описания услуг) и PPTX (маркетинг-киты).<br/>"
         "<b>Решение:</b> Внедрение парсеров на базе <code>pypdf</code>, <code>python-docx</code> и <code>python-pptx</code> с автоматической отправкой извлеченного текста в RAG-документ <code>client_files_{company_name}</code>."),

        ("2. Живой скрапер геосервисов и отзывов (MapsLiveReviewsCollector)",
         "<b>Что требуется:</b> Автоматический сбор свежих отзывов, рейтинга, филиалов и ответов компании с Яндекс.Карт и 2GIS по названию или ссылке.<br/>"
         "<b>Решение:</b> Реализация headless-парсреа на базе <code>Playwright</code> / <code>httpx</code> для извлечения оценок (1-5 звезд) и текста отзывов с последующим анализом болей аудитории в FeedbackLoopEngine."),

        ("3. Расширение сбора внешних соцсетей (Instagram, TikTok, YouTube)",
         "<b>Что требуется:</b> Сбор последних 20–50 постов, шортсов и комментариев из аккаунтов Instagram, TikTok и YouTube.<br/>"
         "<b>Решение:</b> Подключение API/скраперов через ротационные прокси для периодической выгрузки контента и метрик.")
    ]

    for title, desc in missing_points:
        story.append(Paragraph(title, style_h2))
        story.append(Paragraph(desc, style_body))
        story.append(Spacer(1, 4))

    # Сборка документа
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ PDF успешно сгенерирован: {pdf_filename}")
    return pdf_filename


if __name__ == "__main__":
    build_pdf()
