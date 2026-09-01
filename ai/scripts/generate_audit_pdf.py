"""
generate_audit_pdf.py
======================================================================
Генерация расширенного официального PDF-отчета:
"UCust.AI — Аудит готовности архитектуры, Сверх-функционал и Дорожная карта"
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
        self.drawString(1.5 * cm, A4[1] - 1.2 * cm, "UCust.AI — Архитектурный аудит, Сверх-функционал и Roadmap")
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
    
    # Кастомные типографические стили
    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=4
    )
    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=10
    )
    style_h1 = ParagraphStyle(
        "H1",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=10,
        spaceAfter=6
    )
    style_h2_plus = ParagraphStyle(
        "H2Plus",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#047857"), # Зеленый для преимуществ
        spaceBefore=6,
        spaceAfter=2
    )
    style_h2_missing = ParagraphStyle(
        "H2Missing",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#B45309"), # Янтарный для недостающих
        spaceBefore=6,
        spaceAfter=2
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#374151"),
        spaceAfter=4
    )
    style_cell = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1F2937")
    )
    style_cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1F2937")
    )
    style_badge_ready = ParagraphStyle(
        "BadgeReady",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#065F46"),
        alignment=1
    )
    style_badge_partial = ParagraphStyle(
        "BadgePartial",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#92400E"),
        alignment=1
    )

    story = []

    # 1. Титульный блок
    story.append(Paragraph("UCust.AI — Архитектурный аудит и Дорожная карта", style_title))
    story.append(Paragraph("Сравнение с ТЗ, внедренные сверх-возможности (Super-Features) и план боевого автопостинга", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=10))

    # 2. Раздел 1: Сводная таблица готовности
    story.append(Paragraph("1. Сводная таблица готовности по 11 разделам спецификации", style_h1))
    
    table_data = [
        [
            Paragraph("№", style_cell_bold),
            Paragraph("Раздел ТЗ", style_cell_bold),
            Paragraph("Статус", style_cell_bold),
            Paragraph("Реализация в кодовой базе UCust.AI", style_cell_bold)
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
            Paragraph("Рекурсивный обход подстраниц, отсев лого/шапок, отбор товаров, H1-H3, цены, контакты.", style_cell)
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
            Paragraph("Публикация (Execution & Auto-Posting)", style_cell),
            Paragraph("🟨 70%", style_badge_partial),
            Paragraph("Broadcaster отправляет в TG/VK/MAX. Требуется боевая настройка очередей (RabbitMQ/Celery).", style_cell)
        ],
        [
            Paragraph("11", style_cell_bold),
            Paragraph("Анализ обратной связи (Feedback Loop)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("FeedbackLoopEngine — расчет ER, тональность, FAQ/возражения, RAG, адаптация контент-плана.", style_cell)
        ]
    ]

    col_widths = [0.7 * cm, 4.7 * cm, 1.8 * cm, 10.8 * cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    story.append(table)
    story.append(Spacer(1, 8))

    # 3. Раздел 2: Реализовано ЛУЧШЕ, чем в базовом ТЗ (Super-Features)
    story.append(Paragraph("2. Реализовано лучше и глубже, чем в исходном ТЗ (Enterprise Super-Features)", style_h1))
    
    super_features = [
        ("1. Гибридный Clean RAG с BAAI Reranker и 7 категориями памяти",
         "В базовом ТЗ предполагался простой текстовый анализ. Реализован полноценный Enterprise RAG (Dense векторы + BM25 + PostgreSQL pgvector + Кросс-энкодер BGE-Reranker). База разделена на 7 изолированных семантических категорий (Brand DNA, боли ЦА, конкуренты, 3x3 сетка, досье сайта, история фото-промптов, календарь инфоповодов)."),

        ("2. Визуальный арт-дирекшн сетки ленты 3x3 (AdvancedVisualDirector)",
         "Контент-план генерируется не просто плоским списком тем, а с жесткой раскладкой под визуальную сетку 3x3 (чередование макро-деталей, портретов, процессов и товаров) с расчетом брендовой палитры Hex и проверкой цветовой гармонии."),

        ("3. Двухконтурный контроль качества с авто-исправлением (Self-Healing Loop)",
         "Внедрен Агент-Критик (CriticMunger), который оценивает пост по шкале качества. Если текст содержит стоп-слова, панибратство или слабый CTA — он автоматически возвращается автору (SaigaLLM.self_heal_text) на исправление без прерывания пайплайна."),

        ("4. White-Label изоляция и защита коммерческой тайны (SecurityGuard)",
         "Посты для клиентов генерируются в строгом White-Label режиме: специальный гейткипер на лету вырезает и маскирует любые упоминания внутренних моделей (Saiga, FLUX, ComfyUI, Lora, LTX) и исключает корпоративные хэштеги в клиентских каналах."),

        ("5. Умный контентный фильтр медиа сайтов (Anti-Logo & Anti-Banner Filter)",
         "Алгоритм парсера автоматически отсеивает логотипы, шапки сайтов, баннеры и мелкие иконки соцсетей, анализируя размеры (>180x180 px) и пропорции через PIL, отбирая только реальные фотографии товаров и портфолио."),

        ("6. Региональный и отраслевой календарь инфоповодов (EventHolidayCollector)",
         "Встроенный календарь государственных праздников СНГ (РФ, РК, РБ, УЗ), 50+ дней городов и профессиональных праздников по нишам (IT, медицина, автосервис, бьюти, рестораны, стройка). Праздничные дни автоматически встраиваются в 30-дневный контент-план с офферами."),

        ("7. Управление жизненным циклом медиа (MediaRetentionManager)",
         "Временный кэш парсинга автоматически удаляется каждые 5 часов (защита от переполнения диска при 100+ пользователях), а сгенерированные фото/видео архивируются через 30 дней с сохранением финальных промптов в RAG-памяти."),

        ("8. Замкнутый цикл обратной связи и самообучение (FeedbackLoopEngine)",
         "Система собирает комментарии, рассчитывает ER, извлекает частые вопросы покупателей (FAQ) и ключевые возражения («дорого», «гарантия»), а затем автоматически создает посты-ответы в следующем контент-плане.")
    ]

    for title, desc in super_features:
        story.append(Paragraph(f"✨ <b>{title}</b>", style_h2_plus))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 6))

    # 4. Раздел 3: Недостающие элементы и Дорожная карта (Roadmap)
    story.append(Paragraph("3. Недостающие элементы и Дорожная карта реализации (Roadmap до 100%)", style_h1))
    
    missing_items = [
        ("1. Настройка боевого Бэкенд-Автопостинга (Backend Auto-Posting & Scheduler)",
         "<b>Текущее состояние:</b> Каркас отправки (Broadcaster) реализован, но автопостинг требует боевой настройки очереди и управления токенами.<br/>"
         "<b>Что требуется реализовать:</b><br/>"
         "• Интеграция планировщика задач (RabbitMQ + Celery / APScheduler) для публикации ровно по часовому поясу клиента.<br/>"
         "• Шифрованное хранилище токенов доступа клиентов (OAuth 2.0 для VK, Bot Token / MTProto для Telegram).<br/>"
         "• Реализация 2 режимов: <b>«Полный автопилот»</b> (публикация по таймеру) vs <b>«Подтверждение в Telegram»</b> (кнопки Одобрить / Перегенерировать за 30 мин до выхода).<br/>"
         "• Механизм Auto-Retry с экспоненциальной задержкой при лимитах (Rate Limits 429/502)."),

        ("2. Модуль разбора клиентских документов (DocumentCollector)",
         "<b>Что требуется:</b> Извлечение текста и таблиц из загружаемых файлов клиентов (PDF-презентации, DOCX-прайсы, PPTX-маркетинг-киты) через <code>pypdf</code> / <code>python-docx</code> / <code>python-pptx</code> с автоматической индексацией в RAG-документ <code>client_files_{company}</code>."),

        ("3. Живой скрапер карт и отзывов (MapsLiveReviewsCollector)",
         "<b>Что требуется:</b> Headless-парсер Playwright для автоматического сбора живых отзывов, рейтинга и филиалов с Яндекс.Карт и 2GIS для обогащения болей аудитории в FeedbackLoopEngine."),

        ("4. Подключение внешних соцсетей (Instagram, TikTok, YouTube) и статус каналов",
         "<b>Текущие подключенные соцсети системы:</b><br/>"
         "• <b>Telegram:</b> <font color='#2563EB'><u>https://t.me/UcustAi</u></font> (нативный сбор через Telethon и публикация через Bot/MTProto).<br/>"
         "• <b>ВКонтакте (VK):</b> <font color='#2563EB'><u>https://vk.ru/ucustai</u></font> (нативный сбор постов/комментариев и автопостинг через Wall API).<br/>"
         "• <b>MAX:</b> <font color='#2563EB'><u>https://max.ru/channel_UCust</u></font> (интегрированная публикация в корпоративный канал).<br/>"
         "<b>Что требуется подключить дополнительно:</b><br/>"
         "• <b>Instagram:</b> сбор последних 20–50 постов/Reels, вовлеченности (лайки/комментарии) и скрапинг через ротационные прокси.<br/>"
         "• <b>TikTok:</b> парсинг трендовых видео, хэштегов и звуков для обогащения контент-стратегии.<br/>"
         "• <b>YouTube:</b> сбор Shorts и аналитики комментариев для видео-маркетинга.")
    ]

    for title, desc in missing_items:
        story.append(Paragraph(f"⚠️ <b>{title}</b>", style_h2_missing))
        story.append(Paragraph(desc, style_body))

    # Сборка документа
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Расширенный PDF успешно сгенерирован: {pdf_filename}")
    return pdf_filename


if __name__ == "__main__":
    build_pdf()
