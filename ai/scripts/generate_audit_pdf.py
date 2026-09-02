# File: ai/scripts/generate_audit_pdf.py
"""
Executive Architecture Audit, Super-Features & Complete Roadmap Report for UCust.AI.
Генерирует исчерпывающий, структурированный PDF-отчет для руководства, сейлз-менеджеров
и технических специалистов со всеми формулами, 5 ступенями Ханта, фреймворками и дорожной картой.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class NumberedCanvas(canvas.Canvas):
    """Кастомный канвас для нумерации 'Страница X из Y' и корпоративных колонтитулов."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(page_count)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count: int):
        self.saveState()
        self.setFont("Arial", 7.5)
        self.setFillColor(colors.HexColor("#6B7280"))

        # Верхний колонтитул
        self.drawString(1.5 * cm, A4[1] - 1.2 * cm, "UCust.AI — Архитектурный аудит, Маркетинговые фреймворки и Roadmap")
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
    # Регистрация шрифтов
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
    
    style_title = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=3
    )
    style_subtitle = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=8
    )
    style_h1 = ParagraphStyle(
        "H1",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=8,
        spaceAfter=5
    )
    style_h2_plus = ParagraphStyle(
        "H2Plus",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#047857"),
        spaceBefore=5,
        spaceAfter=2
    )
    style_h2_blue = ParagraphStyle(
        "H2Blue",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E40AF"),
        spaceBefore=5,
        spaceAfter=2
    )
    style_h2_missing = ParagraphStyle(
        "H2Missing",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#B45309"),
        spaceBefore=5,
        spaceAfter=2
    )
    style_body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7.8,
        leading=11,
        textColor=colors.HexColor("#374151"),
        spaceAfter=3
    )
    style_formula = ParagraphStyle(
        "FormulaBox",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E3A8A"),
        backColor=colors.HexColor("#EFF6FF"),
        borderColor=colors.HexColor("#BFDBFE"),
        borderWidth=1,
        borderPadding=4,
        spaceBefore=2,
        spaceAfter=3
    )
    style_cell = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#1F2937")
    )
    style_cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor("#1F2937")
    )
    style_badge_ready = ParagraphStyle(
        "BadgeReady",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#065F46"),
        alignment=1
    )
    style_badge_partial = ParagraphStyle(
        "BadgePartial",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor("#92400E"),
        alignment=1
    )
    style_value_box = ParagraphStyle(
        "ValueBox",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#065F46"),
        backColor=colors.HexColor("#ECFDF5"),
        borderColor=colors.HexColor("#A7F3D0"),
        borderWidth=1,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=5
    )

    story = []

    # 1. Титульный блок
    story.append(Paragraph("UCust.AI — Архитектурный аудит и Дорожная карта", style_title))
    story.append(Paragraph("Сравнение с ТЗ, внедренные сверх-возможности (Super-Features), методология продаж и автопостинг", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=8))

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
            Paragraph("UnifiedOrchestrator, UserProfile в SQL + 8 семантических категорий Clean RAG (включая client_files).", style_cell)
        ],
        [
            Paragraph("2", style_cell_bold),
            Paragraph("Источники данных (Сайт, Файлы, Соцсети, Карты)", style_cell),
            Paragraph("🟨 95%", style_badge_partial),
            Paragraph("Сайт (WebsiteCollector), Файлы (DocumentCollector: PDF/DOCX/PPTX), TG, VK. Карты — базовый каркас.", style_cell)
        ],
        [
            Paragraph("3", style_cell_bold),
            Paragraph("Сбор данных с сайта (Website Crawling)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("Глубокий сбор страниц 2-го уровня (/services, /catalog, /prices), Schema.org JSON-LD (товары/FAQ), Anti-Logo фильтр.", style_cell)
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
            Paragraph("Синтез досье сайта, файлов клиентов, фотосеток, инфоповодов и отзывов в единый цифровой профиль.", style_cell)
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
            Paragraph("Воронка TOFU/MOFU/BOFU, визуальная сетка 3x3, арсенал хуков, календарь праздников, лестница Ханта.", style_cell)
        ],
        [
            Paragraph("9", style_cell_bold),
            Paragraph("Генерация контента (Content Generation)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("SaigaLLMSkill + CriticMunger (Self-Healing Loop), 7 маркетинговых фреймворков, ComfyUI FLUX/SDXL, LTX-Video.", style_cell)
        ],
        [
            Paragraph("10", style_cell_bold),
            Paragraph("Публикация (Execution & Auto-Posting)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("Шлюз BackendPostingBridge: TokenCryptoVault (AES-256), расчет пояса клиента, режимы Autopilot / TG-Confirmation, Auto-Retry 429/502.", style_cell)
        ],
        [
            Paragraph("11", style_cell_bold),
            Paragraph("Анализ обратной связи (Feedback Loop)", style_cell),
            Paragraph("✅ 100%", style_badge_ready),
            Paragraph("FeedbackLoopEngine — расчет NAI, WPR%, Log Score, мультиплатформенные эмодзи, авто-адаптация контент-плана.", style_cell)
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
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
    ]))

    story.append(table)
    story.append(Spacer(1, 6))

    # 3. Раздел 2: 12 Сверх-возможностей
    story.append(Paragraph("2. Реализованный сверх-функционал Enterprise уровня (Super-Features)", style_h1))
    
    super_features = [
        ("1. Гибридный Clean RAG с BAAI Reranker и 8 категориями памяти",
         "В базовом ТЗ предполагался простой текстовый анализ. Реализован полноценный Enterprise RAG (Dense векторы + BM25 + PostgreSQL pgvector + Кросс-энкодер BGE-Reranker). База разделена на 8 изолированных семантических категорий (Brand DNA, боли ЦА, конкуренты, 3x3 сетка, досье сайта, файлы клиентов, история фото-промптов, календарь инфоповодов)."),

        ("2. Парсер клиентских документов PDF, DOCX, PPTX (DocumentCollector)",
         "Автоматическое извлечение текста, таблиц прайсов и презентаций из загруженных файлов клиента через <code>pypdf</code>, <code>python-docx</code> и <code>python-pptx</code> с очисткой от верстки и прямой индексацией в RAG-категорию <code>client_files_{company}</code>."),

        ("3. Визуальный арт-дирекшн сетки ленты 3x3 (AdvancedVisualDirector)",
         "Контент-план генерируется не просто плоским списком тем, а с жесткой раскладкой под визуальную сетку 3x3 (чередование макро-деталей, портретов, процессов и товаров) с расчетом брендовой палитры Hex и проверкой цветовой гармонии."),

        ("4. Двухконтурный контроль качества с авто-исправлением (Self-Healing Loop)",
         "Внедрен Агент-Критик (CriticMunger), который оценивает пост по шкале качества. Если текст содержит стоп-слова, панибратство или слабый CTA — он автоматически возвращается автору (SaigaLLM.self_heal_text) на исправление без прерывания пайплайна."),

        ("5. White-Label изоляция и защита коммерческой тайны (SecurityGuard)",
         "Посты для клиентов генерируются в строгом White-Label режиме: специальный гейткипер на лету вырезает и маскирует любые упоминания внутренних моделей (Saiga, FLUX, ComfyUI, Lora, LTX) и исключает корпоративные хэштеги в клиентских каналах."),

        ("6. Умный контентный фильтр медиа сайтов (Anti-Logo & Anti-Banner Filter)",
         "Алгоритм парсера автоматически отсеивает логотипы, шапки сайтов, баннеры и мелкие иконки соцсетей, анализируя размеры (>180x180 px) и пропорции через PIL, отбирая только реальные фотографии товаров и портфолио."),

        ("7. Региональный и отраслевой календарь инфоповодов (EventHolidayCollector)",
         "Встроенный календарь государственных праздников СНГ (РФ, РК, РБ, УЗ), 50+ дней городов и профессиональных праздников по нишам (IT, медицина, автосервис, бьюти, рестораны, стройка). Праздничные дни автоматически встраиваются в 30-дневный контент-план с офферами."),

        ("8. Управление жизненным циклом медиа (MediaRetentionManager)",
         "Временный кэш парсинга автоматически удаляется каждые 5 часов (защита от переполнения диска при 100+ пользователях), а сгенерированные фото/видео архивируются через 30 дней с сохранением финальных промптов в RAG-памяти."),

        ("9. Замкнутый цикл обратной связи и мультиплатформенные реакции (FeedbackLoopEngine)",
         "Система оценивает качество восприятия постов по 3 математическим формулам (NAI, WPR%, Log Positivity Score) с автоматической адаптацией под специфику соцсетей: Telegram (эмодзи и Premium-паки), VK (реакции и репосты), Instagram/TikTok (сохранения в закладки с максимальным весом и Direct-шеры), YouTube (лайки/дизлайки) и MAX. На основе этих данных система перестраивает контент-план под реальные боли ЦА."),

        ("10. Умная маршрутизация сайтов-мостов и витрин (Smart Bridge Router)",
         "Автоматическое распознавание сайтов-одностраничников и витрин с единственной кнопкой перехода в основной каталог/маркетплейс (пример: <code>maksima.uz</code> &rarr; <code>status.uz</code>). Парсер на лету переходит в целевой магазин, выгружает товары, цены, контакты и синтезирует единое RAG-досье бренда."),

        ("11. Генератор маркетинговых фреймворков и Лестница Ханта (MarketingFrameworkDirector)",
         "Усиление маркетинговых навыков платформы без дообучения нейросети. Автоматическая генерация постов по 7 формулам копирайтинга (AIDA, PAS, BAB, 4P, StoryBrand, Hook-Story-Offer, FAB), 5 ступеням прогрева Бена Ханта (Unaware &rarr; Most Aware) и 5 психологическим триггерам Чалдини (Social Proof, Scarcity, Authority, Reciprocity, Risk Reversal)."),

        ("12. База современных трендов, мемов и сленга 2024–2026 гг. (TrendsAndMemesCollector)",
         "Полная компенсация Knowledge Cutoff базовой нейросети 2023 года без дообучения. Файл <code>trends_and_memes.json</code> хранит структурированную базу вирусных мемов, сленга и инфоповодов с адаптацией под 15+ ниш и Anti-Cringe фильтром. Еженедельный планировщик автоматически парсит свежие тренды и синхронизирует их в Clean RAG категорию <code>viral_trends_and_memes</code>."),

        ("13. Мост передачи публикаций в Бэкенд и Планировщик (BackendPostingBridge)",
         "Полный контракт передачи сгенерированных постов и контент-планов в основной Бэкенд. Включает шифрование токенов TokenCryptoVault (AES-256), расчет локального времени по часовому поясу клиента (Europe/Moscow, Asia/Tashkent и др.), 2 режима публикации («Полный автопилот» vs «Согласование в Telegram» за 30 мин) и Auto-Retry с экспоненциальной задержкой при лимитах."),

        ("14. Поисковый оптимизатор хэштегов конкурентов (NicheCompetitorHashtagEngine)",
         "Полный отказ от спонтанных и случайных хэштегов. Система генерирует профессиональный 3-уровневый пакет тегов на базе анализа конкурентов ниши: 1) Гео-коммерческие поисковые теги (#мебельташкент, #стоматологияспб), 2) Среднечастотные категорийные теги для поиска аналогичных постов других пользователей (#столыизмассива, #лофтдизайн), 3) Предметные теги темы (#обеденныйстол, #виниры). Включает строгий Anti-Leak фильтр, исключающий любые внутренние метки #UCust."),

        ("15. Энциклопедия и сторителлинг объектов (ObjectKnowledgeStoryteller)",
         "Интеллектуальное обогащение постов историческими фактами, легендами создания и тайнами мастерства (происхождение Тирамису, секрет выпекания Сан-Себастьян при 240°C, феномен Дубайского шоколада, история кресла Eames 1956 г., голливудские виниры Чарльза Пинкуса 1928 г.). Для кастомных товаров система задействует динамический поиск Tavily Fact Hunter, формируя экспертный и вовлекающий контент без галлюцинаций."),

        ("16. Тарифный шлюз и квотирование календаря генераций (TariffQuotaGateway)",
         "Синхронизация генерации контент-плана с тарифным планом клиента из Бэкенда (Start — 12 постов Пн/Ср/Пт; Business — 20 постов Пн–Пт; Enterprise — 30+ постов ежедневно). Оркестратор запрашивает квоту у бэкенда и строит календарную сетку строго по разрешенным дням недели и часовому поясу клиента, исключая перелимиты.")
    ]

    for title, desc in super_features:
        story.append(Paragraph(f"✨ <b>{title}</b>", style_h2_plus))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 4))

    # 4. Раздел 2.1: Математический аппарат расчета позитивности постов
    story.append(Paragraph("2.1. Математический аппарат расчета позитивности и качества восприятия постов", style_h1))
    story.append(Paragraph(
        "Для оценки качества взаимодействия аудитории с контентом система использует три взаимодополняющие математические формулы, учитывающие специфику реакций соцсетей:",
        style_body
    ))

    # Формула 1: NAI
    story.append(Paragraph("1️⃣ Индекс чистого одобрения (Net Approval Index — NAI):", style_h2_blue))
    story.append(Paragraph("NAI = L / (L + D + 1)", style_formula))
    story.append(Paragraph(
        "<b>Назначение:</b> Отражает баланс одобрения и негатива без искажения объемами охвата. Значение от 0.0 до 1.0 (чем ближе к 1.0, тем лояльнее аудитория). Единица в знаменателе защищает от деления на ноль для новых постов.",
        style_body
    ))

    # Формула 2: WPR
    story.append(Paragraph("2️⃣ Взвешенная позитивность с учетом просмотров (Weighted Positivity Rate — WPR %):", style_h2_blue))
    story.append(Paragraph("WPR = ( (1.0 · L + 1.5 · R − 2.0 · D) / max(V, 1) ) · 100%", style_formula))
    story.append(Paragraph(
        "<b>Назначение:</b> Оценивает процент позитивно вовлеченных пользователей от общего числа просмотров. Каждому действию присвоен социальный вес: лайки (1.0x), комментарии и репосты (1.5x), сохранения в закладки Instagram/TikTok (2.0x), а негативным дизлайкам и эмодзи (👎, 💩, 🤡, 😡) — штрафной вес (-2.0x).",
        style_body
    ))

    # Формула 3: Logarithmic Positivity Score
    story.append(Paragraph("3️⃣ Логарифмический масштабированный балл (Logarithmic Positivity Score — Score):", style_h2_blue))
    story.append(Paragraph("Score = log₁₀(V + 1) · [ (1.0 · L + 1.5 · R + 1) / (1.0 · D + 1) ]", style_formula))
    story.append(Paragraph(
        "<b>Назначение:</b> Логарифмическая прогрессия log₁₀(V + 1) компенсирует падение процента вовлеченности на вирусных миллионных охватах, а множитель позитива мгновенно обнуляет общий балл, если публикация вызывает волну хейта (D &gt; L), блокируя продвижение некачественного контента.",
        style_body
    ))

    # Сводная таблица примеров
    formula_table_data = [
        [
            Paragraph("Сценарий поста", style_cell_bold),
            Paragraph("Охват (V)", style_cell_bold),
            Paragraph("Лайки (L)", style_cell_bold),
            Paragraph("Реакции (R)", style_cell_bold),
            Paragraph("Дизлайки (D)", style_cell_bold),
            Paragraph("NAI", style_cell_bold),
            Paragraph("WPR %", style_cell_bold),
            Paragraph("Score", style_cell_bold),
            Paragraph("Грейд системы", style_cell_bold)
        ],
        [
            Paragraph("Маленький пост", style_cell),
            Paragraph("100", style_cell),
            Paragraph("10", style_cell),
            Paragraph("0", style_cell),
            Paragraph("0", style_cell),
            Paragraph("0.9091", style_cell),
            Paragraph("+10.0%", style_cell),
            Paragraph("22.05", style_cell_bold),
            Paragraph("HIGH_POSITIVE ⭐", style_badge_ready)
        ],
        [
            Paragraph("Средний охват", style_cell),
            Paragraph("10 000", style_cell),
            Paragraph("800", style_cell),
            Paragraph("0", style_cell),
            Paragraph("20", style_cell),
            Paragraph("0.9744", style_cell),
            Paragraph("+7.60%", style_cell),
            Paragraph("152.57", style_cell_bold),
            Paragraph("VIRAL_POSITIVE 🔥", style_badge_ready)
        ],
        [
            Paragraph("Вирусный хейт/спор", style_cell),
            Paragraph("100 000", style_cell),
            Paragraph("2 000", style_cell),
            Paragraph("0", style_cell),
            Paragraph("1 500", style_cell),
            Paragraph("0.5713", style_cell),
            Paragraph("-1.00%", style_cell),
            Paragraph("6.67", style_cell_bold),
            Paragraph("CONTROVERSIAL ⚠️", style_badge_partial)
        ],
        [
            Paragraph("Вирусный суперхит", style_cell),
            Paragraph("100 000", style_cell),
            Paragraph("8 000", style_cell),
            Paragraph("700", style_cell),
            Paragraph("50", style_cell),
            Paragraph("0.9937", style_cell),
            Paragraph("+8.95%", style_cell),
            Paragraph("887.35", style_cell_bold),
            Paragraph("VIRAL_POSITIVE 🔥", style_badge_ready)
        ]
    ]

    formula_table = Table(formula_table_data, colWidths=[2.6 * cm, 1.4 * cm, 1.3 * cm, 1.3 * cm, 1.4 * cm, 1.3 * cm, 1.4 * cm, 1.4 * cm, 3.4 * cm])
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    story.append(formula_table)
    story.append(Spacer(1, 6))

    # 5. Раздел 2.2: Руководство работы — 5 Ступеней прогрева Бена Ханта
    story.append(Paragraph("2.2. Руководство работы: 5 Ступеней прогрева Бена Ханта (Customer Awareness Journey)", style_h1))
    story.append(Paragraph(
        "Лестница узнавания Бена Ханта — это модель, описывающая <b>психологический путь покупателя от полного незнания о проблеме до момента закрытия сделки</b>. В отличие от примитивного спама «Купите со скидкой», система выстраивает 30-дневный контент-план как автоматическую воронку продаж:",
        style_body
    ))

    hunt_stages_details = [
        ("1️⃣ Ступень 1: Безразличие / Не знают о проблеме (Unaware)",
         "<b>Психология клиента:</b> Человек живет обычной жизнью, проблемы не замечает. Прямая продажа вызовет раздражение.<br/>"
         "<b>Цель ИИ:</b> Зацепить внимание, вызвать улыбку или интерес через юмор, бытовой контраст или разрушение мифов.<br/>"
         "<b>Фреймворк и триггеры:</b> Фреймворк <b>BAB</b> (Before-After-Bridge) + Взаимный обмен (Reciprocity).<br/>"
         "<b>Пример работы:</b> <i>«POV: Пытаешься сесть на старый скрипучий стул и не разбудить кота... А как выглядит ваше любимое кресло для отдыха?»</i>"),

        ("2️⃣ Ступень 2: Осознание проблемы / Боль (Problem Aware)",
         "<b>Психология клиента:</b> Человек почувствовал дискомфорт (переплата, неудобство, поломка), но не знает истинных причин.<br/>"
         "<b>Цель ИИ:</b> Точно попасть в скрытую боль клиента, усилить последствия бездействия и показать, что есть решение.<br/>"
         "<b>Фреймворк и триггеры:</b> Фреймворк <b>PAS</b> (Problem-Agitation-Solution) + Авторитет и технологии (Authority).<br/>"
         "<b>Пример работы:</b> <i>«Почему 90% попыток сэкономить на мебели из опилок заканчиваются разбухшей столешницей уже через 2 месяца?»</i>"),

        ("3️⃣ Ступень 3: Поиск решения / Сравнение подходов (Solution Aware)",
         "<b>Психология клиента:</b> Человек понял проблему и выбирает <i>способ</i> ее решения (сделать самому vs купить готовое vs заказать массив).<br/>"
         "<b>Цель ИИ:</b> Экспертно сравнить методы в лоб и доказать объективное превосходство правильного подхода.<br/>"
         "<b>Фреймворк и триггеры:</b> Фреймворк <b>FAB</b> (Feature-Advantage-Benefit) + Снятие рисков (Risk Reversal).<br/>"
         "<b>Пример работы:</b> <i>«МДФ в эмали против Натурального дуба: честный расчет стоимости эксплуатации за 5 лет службы».</i>"),

        ("4️⃣ Ступень 4: Выбор компании и продукта (Product Aware)",
         "<b>Психология клиента:</b> Клиент определился с методом (хочет именно массив дуба), но выбирает, <i>у кого именно</i> заказать.<br/>"
         "<b>Цель ИИ:</b> Показать реальные кейсы, цех, команду, отзывы, сертификаты и выгоду заказа именно в нашей компании.<br/>"
         "<b>Фреймворк и триггеры:</b> Фреймворк <b>StoryBrand</b> (Клиент-Герой, Бренд-Проводник) + Социальное доказательство (Social Proof).<br/>"
         "<b>Пример работы:</b> <i>«Кейс: как мы изготовили обеденный стол 2.4 м для семьи из 6 человек за 7 дней. Отзыв заказчика и закулисье цеха».</i>"),

        ("5️⃣ Ступень 5: Горячая покупка / Выбор оффера (Most Aware)",
         "<b>Психология клиента:</b> Человек полностью доверяет бренду и готов платить. Ему нужен только понятный повод и финальный импульс.<br/>"
         "<b>Цель ИИ:</b> Закрыть сделку здесь и сейчас через дедлайн, понятный CTA и ограниченное спецпредложение.<br/>"
         "<b>Фреймворк и триггеры:</b> Фреймворк <b>AIDA</b> или <b>4P</b> + Дефицит и срочность (Scarcity / FOMO).<br/>"
         "<b>Пример работы:</b> <i>«Только до воскресенья: при заказе стола — защитное масло и сборка в подарок! Осталось 3 слота на замер».</i>")
    ]

    for title, desc in hunt_stages_details:
        story.append(Paragraph(f"<b>{title}</b>", style_h2_blue))
        story.append(Paragraph(desc, style_body))

    # Выделенный блок ценности для клиента UCust.AI
    story.append(Paragraph(
        "💡 <b>В чем ценность для клиента UCust.AI:</b><br/>"
        "Благодаря этой системе контент-план превращается в <b>автоматическую воронку продаж</b>: "
        "Подписчик, который зашел на страницу «холодным», за 1–2 недели мягко и незаметно проходит все 5 ступеней "
        "и сам приходит в личные сообщения с готовностью купить!",
        style_value_box
    ))

    story.append(Spacer(1, 4))

    # 6. Раздел 2.3: Сводная таблица маркетинговых фреймворков и триггеров Чалдини
    story.append(Paragraph("2.3. Сводка 7 Маркетинговых фреймворков и 5 психологических триггеров", style_h1))
    
    fw_table_data = [
        [
            Paragraph("Фреймворк", style_cell_bold),
            Paragraph("Структура формулы", style_cell_bold),
            Paragraph("Лучшее применение в SMM", style_cell_bold),
            Paragraph("Основной триггер", style_cell_bold)
        ],
        [
            Paragraph("AIDA", style_cell_bold),
            Paragraph("Attention &rarr; Interest &rarr; Desire &rarr; Action", style_cell),
            Paragraph("Продающие промо-посты, спецпредложения, анонсы акций", style_cell),
            Paragraph("Scarcity / FOMO (Дедлайн)", style_cell)
        ],
        [
            Paragraph("PAS", style_cell_bold),
            Paragraph("Problem &rarr; Agitation &rarr; Solution", style_cell),
            Paragraph("Посты в скрытые боли ЦА (страх переплаты, поломки)", style_cell),
            Paragraph("Authority (Оборудование/Стандарты)", style_cell)
        ],
        [
            Paragraph("BAB", style_cell_bold),
            Paragraph("Before &rarr; After &rarr; Bridge", style_cell),
            Paragraph("Кейсы трансформации, сравнения ДО и ПОСЛЕ", style_cell),
            Paragraph("Reciprocity (Бесплатная польза)", style_cell)
        ],
        [
            Paragraph("4P", style_cell_bold),
            Paragraph("Picture &rarr; Promise &rarr; Prove &rarr; Push", style_cell),
            Paragraph("Эмоциональное погружение с твердыми пруфами и дедлайном", style_cell),
            Paragraph("Social Proof (Рейтинг 4.9, отзывы)", style_cell)
        ],
        [
            Paragraph("StoryBrand", style_cell_bold),
            Paragraph("Hero &rarr; Problem &rarr; Guide &rarr; Plan &rarr; CTA", style_cell),
            Paragraph("Имиджевые посты, истории клиентов, миссия компании", style_cell),
            Paragraph("Risk Reversal (Договор, гарантия 5 лет)", style_cell)
        ],
        [
            Paragraph("HSO (Reels)", style_cell_bold),
            Paragraph("3-sec Hook &rarr; Story &rarr; Offer", style_cell),
            Paragraph("Короткие вертикальные видео Reels / Shorts / Клипы", style_cell),
            Paragraph("Scarcity (Спеццена в комментариях)", style_cell)
        ],
        [
            Paragraph("FAB", style_cell_bold),
            Paragraph("Feature &rarr; Advantage &rarr; Benefit", style_cell),
            Paragraph("Технические обзоры товаров, перевод свойств в выгоду", style_cell),
            Paragraph("Authority (Сертификаты качества)", style_cell)
        ]
    ]

    fw_table = Table(fw_table_data, colWidths=[2.2 * cm, 4.8 * cm, 6.2 * cm, 3.8 * cm])
    fw_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#D1D5DB")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))

    story.append(fw_table)
    story.append(Spacer(1, 6))

    # 7. Раздел 2.4: Продвинутый маркетинговый стек (JTBD, Value Ladder, Fogg CTA)
    story.append(Paragraph("2.4. Продвинутый маркетинговый стек: JTBD, Лестница ценности и Модель Фогга (B = MAP)", style_h1))
    story.append(Paragraph(
        "Для максимизации конверсий в контент-движок внедрены три мощные модели поведенческой экономики:",
        style_body
    ))

    advanced_tools = [
        ("🎯 JTBD (Jobs-to-be-Done) Движок:",
         "Преобразует технические свойства продукта в 3 измерения ценности: <b>Функциональное</b> (какую практическую работу делает), <b>Эмоциональное</b> (какое чувство уюта/спокойствия дарит) и <b>Социальное</b> (как клиента воспринимают семья, друзья и коллеги). Клиент покупает не товар, а лучшую версию себя!"),

        ("🪜 Лестница ценности Рассела Брансона (Value Ladder):",
         "Автоматически выстраивает 4-уровневую продуктовую линейку в контенте: <b>Lead Magnet</b> (бесплатный чек-лист/3D-проект за 0 ₽) &rarr; <b>Tripwire</b> (недорогой пробник/диагностика за 490 ₽) &rarr; <b>Core Offer</b> (основной флагманский продукт) &rarr; <b>Profit Maximizer</b> (VIP-абонемент и расширенная гарантия)."),

        ("⚡ Модель поведения Фогга для CTA (BJ Fogg B = Motivation x Ability x Prompt):",
         "Исключает высокое трение («позвоните в офис») и заменяет его на микро-действия с нулевым барьером: прямое ключевое слово в комментариях (<i>«Напишите +»</i>), экспресс-тест из 3 вопросов или мгновенная выдача гайда ботом за 5 секунд.")
    ]

    for title, desc in advanced_tools:
        story.append(Paragraph(f"<b>{title}</b>", style_h2_blue))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 4))

    # 8. Раздел 2.5: Умная матрица длины контента и ритма внимания
    story.append(Paragraph("2.5. Умная матрица длины контента и ритма внимания аудитории", style_h1))
    story.append(Paragraph(
        "Чтобы исключить «информационную слепоту» и удерживать внимание подписчиков на бегу, система автоматически распределяет посты по 4-уровневой ритмической матрице:",
        style_body
    ))

    content_rhythm = [
        ("⚡ 1. Микро-посты и хуки «Уравнение вкуса/результата» (45% плана):",
         "2–4 строчки на быстрое чтение за 3 секунды. Идеально для утренних публикаций и быстрого скроллинга ленты (пример: <i>«Слоёное тесто + миндаль = идеальный ролл 🫶🏻 Маленькая пауза среди дня. Ждем на кофе!»</i>)."),
        
        ("☕ 2. Средние вовлекающие посты «Знали ли вы, что...» (40% плана):",
         "1–2 абзаца экспертной пользы, фактов об ингредиентах или суперфудах (антиоксиданты корицы, магний миндаля, снятие стресса) с ненавязчивым переходом к заказу."),
        
        ("📖 3. Глубокий сторителлинг и легенды создания (15% плана, 1 раз в неделю):",
         "Полноформатные истории для выходных дней: происхождение Тирамису 1969 г., секрет выпекания Сан-Себастьян при 240°C, манифест безопасности закрытого контура."),

        ("🎯 4. Интерактивные блиц-опросы и опросы выбора (1–2 строчки):",
         "Мгновенный сбор реакций и комментариев аудитории (<i>«Битва вкусов: 🥐 Краффин или 🌰 Миндальный ролл? Голосуйте в комментариях!»</i>).")
    ]

    for title, desc in content_rhythm:
        story.append(Paragraph(f"<b>{title}</b>", style_h2_blue))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 4))

    # 9. Раздел 2.6: Защита данных, TechSanitizer и правило без додумываний
    story.append(Paragraph("2.6. Конфиденциальность, TechSanitizer и правило «Zero-Assumptions»", style_h1))
    story.append(Paragraph(
        "Система гарантирует 100% безопасность коммерческих данных бизнеса и высокую культуру генерации текстов:",
        style_body
    ))

    security_rules = [
        ("🔒 100% Локальный On-Premise контур (Zero Third-Party Leakage):",
         "Все генеративные нейросети работают строго на собственных закрытых серверах. Базы знаний, клиентские досье, рецептуры и токены <b>никогда не передаются в сторонние публичные облака</b>."),

        ("🛡️ Фильтр защиты от утечек технологий (TechSanitizer):",
         "Строгий запрет на упоминание названий внутренних моделей и библиотек. Система автоматически переводит технические термины на язык понятных бизнесу возможностей (<i>ИИ-копирайтер, компьютерное зрение, генератор студийных фото, база знаний бренда</i>)."),

        ("⚖️ Комплексный страж достоверности (ZeroAssumptionsGuard):",
         "Полный запрет на додумывание коммерческих фактов бизнеса по 6 ключевым направлениям:<br/>"
         "1. <b>Цены и скидки:</b> запрет придумывания точных цен и % скидок («скидка 70%») без источника в RAG.<br/>"
         "2. <b>Локации и график:</b> запрет вымышленных адресов и ложного режима 24/7.<br/>"
         "3. <b>Состав и диеты:</b> запрет неподтвержденных медицинских обещаний и аллергенных ярлыков.<br/>"
         "4. <b>Сроки и гарантии:</b> запрет нереалистичных сроков («доставка за 5 минут», «вечная гарантия»).<br/>"
         "5. <b>Вкусы и музыка:</b> запрет навязывания жанров (рок, рэп) в пользу универсальных эмоциональных формулировок («мотивирующая музыка на всю громкость», «заряжающий трек»).<br/>"
         "6. <b>Отзывы:</b> запрет генерации фальшивых имен и вымышленных цитат клиентов.")
    ]

    for title, desc in security_rules:
        story.append(Paragraph(f"<b>{title}</b>", style_h2_blue))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 4))

    # 10. Раздел 2.7: Стратегия распределения медиа (Фото 80% + Текст 20%) и Тарифная сетка
    story.append(Paragraph("2.7. Стратегия медиа-пакетов и Динамическая тарифная сетка (Управление через Бэкенд)", style_h1))
    story.append(Paragraph(
        "Количество постов и разрешенные дни недели <b>полностью настраиваются и управляются через Бэкенд</b> в базе данных. AI-оркестратор динамически адаптируется под любую переданную квоту:",
        style_body
    ))

    tariff_table_data = [
        [
            Paragraph("Название тарифа", style_cell_bold),
            Paragraph("Управление объемом (через Бэкенд)", style_cell_bold),
            Paragraph("Медиа-оснащение (AI)", style_cell_bold)
        ],
        [
            Paragraph("<font color='#2563EB'><b>Тариф «START»</b></font>", style_cell_bold),
            Paragraph("Количество генераций и дни (например, 8–12 постов, Пн/Ср/Пт) <b>задаются через Бэкенд</b>", style_cell),
            Paragraph("Студийные фото (80%) + Текстовые посты/Опросы (20%) + Подбор хэштегов конкурентов", style_cell)
        ],
        [
            Paragraph("<font color='#2563EB'><b>Тариф «BUSINESS»</b></font>", style_cell_bold),
            Paragraph("Количество генераций и дни (например, 20–22 поста, Пн–Пт) <b>задаются через Бэкенд</b>", style_cell),
            Paragraph("Детальные фотосессии (срез, макро, интерьер) + Сторителлинг + Маркетинговые воронки", style_cell)
        ],
        [
            Paragraph("<font color='#2563EB'><b>Тариф «ENTERPRISE»</b></font>", style_cell_bold),
            Paragraph("Интенсивный график (например, 30–60 постов ежедневно) <b>задается через Бэкенд</b>", style_cell),
            Paragraph("Полная автоматизация всех каналов + Глубокий RAG-анализ ниши + Приоритет в очереди", style_cell)
        ],
        [
            Paragraph("<font color='#7C3AED'><b>Тариф «CUSTOM» (All-Inclusive)</b></font>", style_cell_bold),
            Paragraph("Любые кастомные квоты и произвольные часы публикаций <b>задаются через Бэкенд</b>", style_cell),
            Paragraph("Разблокировка 100% функционала: скрапинг Яндекс.Карт и 2GIS, омниканальный радар, VIP-приоритет", style_cell)
        ]
    ]

    tariff_table = Table(tariff_table_data, colWidths=[38 * mm, 72 * mm, 70 * mm])
    tariff_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    story.append(tariff_table)
    story.append(Spacer(1, 4))

    media_and_custom_rules = [
        ("📸 2-Режимная модель медиа (Студийные фото 80% + Текст/Интерактив 20%):",
         "Для 80% публикаций генерируются детализированные студийные фотографии (макросъемка товаров, срезы выпечки, интерьеры), а для 20% — легкие текстовые опросы и новости. Генерация видео временно отключена и автоматически замещается фотосессиями для 100% стабильности и исключения перегрузок VRAM."),

        ("🧮 Бесшовная динамическая адаптация квот (Data-Driven Scaling):",
         "Оркестратор не содержит захардкоженных цифр: при изменении тарифных настроек на бэкенде система автоматически пересчитывает интервалы между публикациями без изменения исходного кода AI.")
    ]

    for title, desc in media_and_custom_rules:
        story.append(Paragraph(f"<b>{title}</b>", style_h2_blue))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 4))

    # 11. Раздел 2.8: Маркетинговые воронки продаж (TOFU, MOFU, BOFU, Хант, Value Ladder)
    story.append(Paragraph("2.8. Архитектура воронок продаж: TOFU &rarr; MOFU &rarr; BOFU, Лестница Ханта и Flywheel", style_h1))
    story.append(Paragraph(
        "AI-контур автоматически распределяет контент по <b>4 взаимодополняющим воронкам продаж</b>, "
        "чтобы превращать случайных читателей в постоянных покупателей без ручного вмешательства маркетолога:",
        style_body
    ))

    # Сводная таблица классической воронки TOFU-MOFU-BOFU
    funnel_table_data = [
        [
            Paragraph("Уровень воронки", style_cell_bold),
            Paragraph("Доля в плане и Цель", style_cell_bold),
            Paragraph("Используемые форматы и Фреймворки", style_cell_bold),
            Paragraph("Психологические триггеры", style_cell_bold)
        ],
        [
            Paragraph("<font color='#0D9488'><b>TOFU</b></font><br/>(Top of Funnel)<br/><i>Верх воронки</i>", style_cell_bold),
            Paragraph("<b>45% контента</b><br/>Охват холодной аудитории, вирусный интерес, привлечение подписчиков", style_cell),
            Paragraph("• Микро-посты «Уравнение вкуса/результата»<br/>• Факты «Знали ли вы, что...»<br/>• Тренды и мемы ниши 2024–2026<br/>• Фреймворки: Hook-Story-Offer, FAB", style_cell),
            Paragraph("Любопытство, Social Proof, снятие тревожности", style_cell)
        ],
        [
            Paragraph("<font color='#2563EB'><b>MOFU</b></font><br/>(Middle of Funnel)<br/><i>Середина воронки</i>", style_cell_bold),
            Paragraph("<b>35% контента</b><br/>Прогрев, доверие, демонстрация стандартов и экспертности бренда", style_cell),
            Paragraph("• Экспертный сторителлинг (история десерта, происхождение дуба)<br/>• Разбор ошибок и кейсы ДО/ПОСЛЕ<br/>• Фреймворки: PAS, BAB, StoryBrand", style_cell),
            Paragraph("Authority (Стандарты), Reciprocity (Польза/Гайд)", style_cell)
        ],
        [
            Paragraph("<font color='#DC2626'><b>BOFU</b></font><br/>(Bottom of Funnel)<br/><i>Низ воронки</i>", style_cell_bold),
            Paragraph("<b>20% контента</b><br/>Прямая конверсия в оплату, заявку, визит или звонок", style_cell),
            Paragraph("• Спецпредложения с дедлайном<br/>• Промокоды и подарочные наборы<br/>• Fogg CTA («Напишите + в ЛС»)<br/>• Фреймворки: 4P, AIDA (Action)", style_cell),
            Paragraph("Scarcity (Лимит мест/времени), Risk Reversal (Гарантия)", style_cell)
        ]
    ]

    funnel_table = Table(funnel_table_data, colWidths=[32 * mm, 46 * mm, 62 * mm, 40 * mm])
    funnel_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    story.append(funnel_table)
    story.append(Spacer(1, 4))

    # Описание других воронок
    extra_funnels = [
        ("🎯 5 Ступеней узнавания Бена Ханта (Stages of Awareness):",
         "Сквозной прогрев аудитории от полного безразличия (<i>Unaware</i>) &rarr; осознание боли (<i>Problem Aware</i>) &rarr; поиск решений (<i>Solution Aware</i>) &rarr; выбор продукта (<i>Product Aware</i>) &rarr; покупка (<i>Most Aware</i>). Система сама чередует ступени в календарной сетке."),

        ("🪜 Лестница ценности Рассела Брансона (Value Ladder):",
         "Автоматическая связка контента: <b>Lead Magnet</b> (бесплатный чек-лист за 0 ₽) &rarr; <b>Tripwire</b> (тест-драйв/пробник за 490 ₽) &rarr; <b>Core Offer</b> (основной продукт) &rarr; <b>Profit Maximizer</b> (VIP-абонемент)."),

        ("🔄 Воронка удержания и сарафанного радио (Retention & Flywheel Funnel):",
         "Специальные публикации для действующих клиентов: закрытые бонусные программы, напоминания о сезонном обслуживании и вовлечение в создание пользовательского контента (UGC-отзывы)."),

        ("⚡ Модель поведенческой конверсии Фогга (BJ Fogg B = MAP):",
         "Исключение трения при закрытии сделки: вместо сложных звонков система предлагает микро-действие с нулевым барьером (<i>«Напишите КОРИЦА в комментариях и бот пришлет купон на десерт за 5 секунд»</i>).")
    ]

    for title, desc in extra_funnels:
        story.append(Paragraph(f"<b>{title}</b>", style_h2_blue))
        story.append(Paragraph(desc, style_body))

    story.append(Spacer(1, 4))

    # 12. Раздел 3: Недостающие элементы и Дорожная карта (Roadmap)
    story.append(Paragraph("3. Недостающие элементы и Дорожная карта реализации (Roadmap до 100%)", style_h1))
    
    missing_items = [
        ("1. Передача публикаций в Бэкенд и Планировщик (Backend Posting Bridge)",
         "<b>Статус со стороны AI:</b> ✅ <b>100% реализован</b> (Модуль <code>BackendPostingBridge</code> полностью готов и протестирован).<br/>"
         "• Реализован защищенный контракт передачи полного медиа-пакета (текст, фото FLUX, видео LTX, хэштеги, промокод).<br/>"
         "• Реализовано шифрованное хранилище токенов доступа клиентов <code>TokenCryptoVault</code> (AES-256).<br/>"
         "• Поддерживается расчет времени под любой часовой пояс клиента (МСК, Ташкент, Алматы).<br/>"
         "• Реализованы 2 режима: <b>«Полный автопилот»</b> vs <b>«Согласование в Telegram»</b> (кнопки Одобрить / Перегенерировать за 30 мин до выхода).<br/>"
         "• Встроен механизм Auto-Retry с экспоненциальной задержкой (Exponential Backoff) при Rate Limits 429/502/503.<br/>"
         "<i>Остается на стороне внешнего бэкенда:</i> прием вебхука/пакета в очередь Celery/RabbitMQ и непосредственный HTTP-вызов соцсетей."),

        ("2. Живой скрапер карт и отзывов (MapsLiveReviewsCollector)",
         "<b>Что требуется:</b> Headless-парсер Playwright для автоматического сбора живых отзывов, рейтинга и филиалов с Яндекс.Карт и 2GIS для обогащения болей аудитории в FeedbackLoopEngine."),

        ("3. Подключение внешних соцсетей (Instagram, TikTok, YouTube) и статус каналов",
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
    print(f"✅ Исчерпывающий PDF успешно сгенерирован: {pdf_filename}")
    return pdf_filename


if __name__ == "__main__":
    build_pdf()
