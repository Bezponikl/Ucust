# -*- coding: utf-8 -*-
"""
Генератор PDF-руководства по интеграции Бэкенда с AI Оркестратором UCust.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def register_fonts():
    font_dir = "C:/Windows/Fonts"
    arial_regular = os.path.join(font_dir, "arial.ttf")
    arial_bold = os.path.join(font_dir, "arialbd.ttf")
    arial_italic = os.path.join(font_dir, "ariali.ttf")
    
    pdfmetrics.registerFont(TTFont("ArialCustom", arial_regular))
    pdfmetrics.registerFont(TTFont("ArialCustom-Bold", arial_bold))
    pdfmetrics.registerFont(TTFont("ArialCustom-Italic", arial_italic))

class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("ArialCustom", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header line (pages > 1)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(15 * mm, 285 * mm, 195 * mm, 285 * mm)
            self.drawString(15 * mm, 287 * mm, "UCust.AI — Руководство по интеграции единого шлюза Оркестратора")
            self.drawRightString(195 * mm, 287 * mm, "v2.5.0 Enterprise")

        # Footer
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(15 * mm, 15 * mm, 195 * mm, 15 * mm)
        self.drawString(15 * mm, 10 * mm, "Конфиденциально • UCust Multi-Server Architecture (WireGuard Private Protocol)")
        page_text = f"Стр. {self._pageNumber} из {page_count}"
        self.drawRightString(195 * mm, 10 * mm, page_text)
        self.restoreState()

def create_pdf(output_path="UCust_AI_Backend_Integration_Guide.pdf"):
    register_fonts()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='ArialCustom-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='ArialCustom',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Header1',
        fontName='ArialCustom-Bold',
        fontSize=12.5,
        leading=15.5,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        fontName='ArialCustom-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        fontName='ArialCustom',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        fontName='ArialCustom',
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor('#0f172a')
    )

    table_header_style = ParagraphStyle(
        'TH',
        fontName='ArialCustom-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )

    story = []
    # =============================================================
    # СТРАНИЦА 1: ТИТУЛ, АРХИТЕКТУРА И .ENV
    # =============================================================
    story.append(Paragraph("UCust.AI — Памятка интеграции с Бэкендом & RAG/SQL", title_style))
    story.append(Paragraph("Архитектура единого шлюза Оркестратора, синхронизация с базой знаний и PostgreSQL + pgvector", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3b82f6'), spaceAfter=10))

    story.append(Paragraph("1. Архитектура взаимодействия сервисов", h1_style))
    story.append(Paragraph(
        "Все микросервисы и пайплайны искусственного интеллекта (парсеры, Moondream, Saiga LLM, ComfyUI, RAG, DLP) "
        "объединены за <b>Единым Универсальным Шлюзом Оркестратора</b>. Бэкенду не требуется знать адреса десятков микросервисов — "
        "общение происходит через один защищенный эндпоинт по приватному каналу WireGuard.",
        body_style
    ))

    # Схема архитектуры
    arch_box = [
        [
            Paragraph(
                "<b>[ Frontend (React / Web) ]</b>  <br/>"
                "  ├── 1. Ввод ссылок / Заполнение анкеты  ──>  <b>[ Java / Node.js Backend ]</b><br/>"
                "  ├── 2. Загрузка фото & прайсов (Drag&Drop)  ───────┤<br/>"
                "  └── 3. Просмотр готового контент-плана & витрины ───┤<br/>"
                "                                                      │ (POST /api/v1/orchestrator/execute)<br/>"
                "                                                      ▼ (X-Internal-Secret + WireGuard 10.0.0.x)<br/>"
                "<b>[ AI Universal Gateway (FastAPI Orchestrator) ]</b><br/>"
                "  ├── <b>⚡ Moondream VLM</b>: мгновенный пре-анализ фото и палитры при загрузке<br/>"
                "  ├── <b>🌐 Collectors & Parsers</b>: сбор данных (VK, TG, Web, 2GIS, PDF/DOCX прайсы)<br/>"
                "  ├── <b>📚 Clean RAG & SQL</b>: векторизация фактов, гибридный поиск, HNSW в PostgreSQL<br/>"
                "  ├── <b>✍️ Saiga LLM</b>: генерация текста, воронки Ханта, контент-стратегия, DLP<br/>"
                "  └── <b>🎨 ComfyUI Diffusion</b>: синтез реалистичных фото (Realism 2.0 SDXL / LTX)<br/>"
                "                                                      │<br/>"
                "  └── <b>[ Фоновый Auto-Push Webhook ]</b> ────────────┘ (JAVA_BACKEND_CALLBACK_URL)",
                code_style
            )
        ]
    ]
    arch_table = Table(arch_box, colWidths=[180 * mm])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 8))

    # Переменные окружения (.env)
    story.append(Paragraph("2. Конфигурация окружения (.env)", h1_style))
    
    env_data = [
        [Paragraph("Переменная", table_header_style), Paragraph("Где задается", table_header_style), Paragraph("Назначение и пример значения", table_header_style)],
        [
            Paragraph("<code>AI_ORCHESTRATOR_ENDPOINT</code>", code_style),
            Paragraph("Бэкенд (.env)", body_style),
            Paragraph("<code>http://10.0.0.2:8000/api/v1/orchestrator/execute</code><br/>Единая точка входа для всех AI-задач.", body_style)
        ],
        [
            Paragraph("<code>INTERNAL_API_SECRET</code>", code_style),
            Paragraph("Бэкенд & AI", body_style),
            Paragraph("<code>ucust-super-secret-service-token-2026</code><br/>Секретный токен для заголовка <code>X-Internal-Secret</code>.", body_style)
        ],
        [
            Paragraph("<code>JAVA_BACKEND_CALLBACK_URL</code>", code_style),
            Paragraph("AI (.env)", body_style),
            Paragraph("<code>http://10.0.0.1:8080/api/v1/ai/callback</code><br/>Webhook для фонового автопуша готовых постов и задач.", body_style)
        ],
        [
            Paragraph("<code>DATABASE_URL</code>", code_style),
            Paragraph("Бэкенд & AI", body_style),
            Paragraph("<code>postgresql://ucust_app:pass@10.0.0.1:5432/ucust_db</code><br/>Подключение к PostgreSQL с расширением pgvector.", body_style)
        ],
        [
            Paragraph("<code>ENABLE_AUTO_PUSH_TO_BACKEND</code>", code_style),
            Paragraph("AI (.env)", body_style),
            Paragraph("<code>true</code> — автоматическая фоновая отправка результатов в БД бэка.", body_style)
        ],
    ]
    env_table = Table(env_data, colWidths=[55 * mm, 30 * mm, 95 * mm])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(env_table)

    story.append(PageBreak())

    # =============================================================
    # СТРАНИЦА 2: КАТАЛОГ КОМАНД И ЕДИНЫЙ КОНТРАКТ
    # =============================================================
    story.append(Paragraph("3. Каталог задач Единого Шлюза Оркестратора", h1_style))
    story.append(Paragraph(
        "Бэкенд отправляет <code>POST /api/v1/orchestrator/execute</code>, передавая в теле имя команды <code>task_type</code>:",
        body_style
    ))

    tasks_data = [
        [Paragraph("task_type", table_header_style), Paragraph("Что выполняет AI под капотом", table_header_style), Paragraph("Когда вызывать бэкенду", table_header_style), Paragraph("SLA времени", table_header_style)],
        [
            Paragraph("<b>quick_vision</b>", ParagraphStyle('T1', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Moondream VLM мгновенно сканирует фото, извлекает палитру, роли (руки, товар, фон) и распределяет слоты нод 55, 64, 65.", body_style),
            Paragraph("При загрузке/перетаскивании фото в UI.", body_style),
            Paragraph("<b>0.2 - 0.5 сек</b>", body_style)
        ],
        [
            Paragraph("<b>analyze_documents</b>", ParagraphStyle('T2', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("DocumentCollector извлекает таблицы и текст из PDF, DOCX, XLSX и сразу индексирует их в RAG/SQL память бренда.", body_style),
            Paragraph("При прикреплении файлов прайса/каталога.", body_style),
            Paragraph("<b>0.3 - 0.9 сек</b>", body_style)
        ],
        [
            Paragraph("<b>quick_scan</b>", ParagraphStyle('T3', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Параллельный скан сайта, VK, 2GIS/Яндекс: моментальное автозаполнение названия, логотипа, цветов, УТП и отзывов.", body_style),
            Paragraph("При вводе ссылок на шаге 1 анкеты.", body_style),
            Paragraph("<b>0.4 - 0.8 сек</b>", body_style)
        ],
        [
            Paragraph("<b>rag_ingest</b>", ParagraphStyle('TR1', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#7c3aed'))),
            Paragraph("Прямая индексация фактов, правил бренда и акций в PostgreSQL + pgvector с нарезкой по 350 токенов и изоляцией tenant_id.", body_style),
            Paragraph("При сохранении настроек/информации о бренде.", body_style),
            Paragraph("<b>0.1 - 0.3 сек</b>", body_style)
        ],
        [
            Paragraph("<b>rag_query</b>", ParagraphStyle('TR2', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#7c3aed'))),
            Paragraph("Гибридный поиск (BM25 + Cosine Distance <=> в SQL) + Кросс-энкодер реранкер (BGE) + Anti-Hallucination Guard.", body_style),
            Paragraph("При поиске фактов/ответов по базе знаний.", body_style),
            Paragraph("<b>< 0.15 сек</b>", body_style)
        ],
        [
            Paragraph("<b>onboard_user</b>", ParagraphStyle('T4', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Глубокий анализ профиля: составление контент-стратегии 3x3, ЦА, SWOT, тональности и полной базы RAG бренда.", body_style),
            Paragraph("При завершении регистрации/онбординга.", body_style),
            Paragraph("<b>1.5 - 3.0 сек</b>", body_style)
        ],
        [
            Paragraph("<b>generate_post</b>", ParagraphStyle('T5', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#059669'))),
            Paragraph("Сквозной синтез: Saiga LLM (текст + Хант-воронка + RAG-факты) ⨂ ComfyUI Diffuse (кадр realism2.0) + Pre-Mortem Критик.", body_style),
            Paragraph("По кнопке «Создать пост» / по расписанию.", body_style),
            Paragraph("<b>2.0 - 5.0 сек</b>", body_style)
        ],
        [
            Paragraph("<b>plan_content</b>", ParagraphStyle('T6', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("ContentStrategyEngine формирует календарь постов на N дней с учетом праздников, болей аудитории и сетки 3x3.", body_style),
            Paragraph("При запросе контент-плана на неделю/месяц.", body_style),
            Paragraph("<b>0.8 - 1.5 сек</b>", body_style)
        ],
        [
            Paragraph("<b>get_graph_data</b>", ParagraphStyle('T7', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Security DLP: отдает очищенные от PII данные для интерактивных графиков и витрины аналитики в интерфейсе.", body_style),
            Paragraph("При открытии дашборда аналитики.", body_style),
            Paragraph("<b>< 0.1 сек</b>", body_style)
        ],
    ]
    tasks_table = Table(tasks_data, colWidths=[31 * mm, 81 * mm, 46 * mm, 22 * mm])
    tasks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tasks_table)

    story.append(PageBreak())

    # =============================================================
    # СТРАНИЦА 3: ПОШАГОВЫЕ СЦЕНАРИИ (JSON DTO)
    # =============================================================
    story.append(Paragraph("4. Пошаговые сценарии и контракты данных (JSON DTO)", h1_style))

    # Сценарий 1
    story.append(Paragraph("📌 Сценарий 1: Быстрый скан ссылок при вводе в анкету (quick_scan)", h2_style))
    story.append(Paragraph("Бэкенд отправляет запрос на шлюз сразу при вставке ссылки пользователем:", body_style))
    
    s1_req = (
        "// POST /api/v1/orchestrator/execute\n"
        "{\n"
        '  "task_type": "quick_scan",\n'
        '  "user_id": "usr_102",\n'
        '  "payload": {\n'
        '    "urls": ["https://maisoncafe.ru", "https://vk.com/maison_cafe"],\n'
        '    "city": "Москва"\n'
        '  }\n'
        "}"
    )
    s1_res = (
        "// ОТВЕТ ОРКЕСТРАТОРА (JSON):\n"
        "{\n"
        '  "status": "success", "task_type": "quick_scan",\n'
        '  "data": {\n'
        '    "prefilled_profile": {\n'
        '      "business_name": "Maison Cafe",\n'
        '      "niche": "Крафтовая кофейня",\n'
        '      "brand_colors": ["#8B5A2B", "#D2B48C", "#FFF8DC"],\n'
        '      "description": "Спешелти кофе свежей обжарки.",\n'
        '      "reviews_summary": "Рейтинг 4.9. Хвалят авторский капучино."\n'
        '    }\n'
        '  }\n'
        "}"
    )
    code_t1 = Table([[Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ЗАПРОС БЭКЕНДА:</b><br/>{s1_req.replace(chr(10), '<br/>')}</font>", code_style),
                      Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ОТВЕТ AI:</b><br/>{s1_res.replace(chr(10), '<br/>')}</font>", code_style)]],
                    colWidths=[90 * mm, 90 * mm])
    code_t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(code_t1)
    story.append(Spacer(1, 6))

    # Сценарий 2
    story.append(Paragraph("📌 Сценарий 2: Моментальный анализ фото при загрузке (quick_vision)", h2_style))
    story.append(Paragraph("Отправляется в момент прикрепления фото пользователем, чтобы не ждать при генерации поста:", body_style))
    
    s2_req = (
        "{\n"
        '  "task_type": "quick_vision",\n'
        '  "user_id": "usr_102",\n'
        '  "payload": {\n'
        '    "attachments": ["https://s3.ucust.ai/uploads/hands.png", "https://s3.ucust.ai/uploads/husky.png", "https://s3.ucust.ai/uploads/cafe.png"]\n'
        '  }\n'
        "}"
    )
    s2_res = (
        "{\n"
        '  "status": "success", "task_type": "quick_vision",\n'
        '  "data": {\n'
        '    "slot_mapping": {\n'
        '      "image1_node55": {"label": "Руки с маникюром в свитере", "role": "hands_body"},\n'
        '      "image2_node64": {"label": "Собака породы хаски", "role": "pet_animal"},\n'
        '      "image3_node65": {"label": "Интерьер кофейни с чашкой кофе", "role": "environment"}\n'
        '    },\n'
        '    "visual_narrative": "Сцена: девушка держит хаски за столом в кофейне..."\n'
        '  }\n'
        "}"
    )
    code_t2 = Table([[Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ЗАПРОС БЭКЕНДА:</b><br/>{s2_req.replace(chr(10), '<br/>')}</font>", code_style),
                      Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ОТВЕТ AI:</b><br/>{s2_res.replace(chr(10), '<br/>')}</font>", code_style)]],
                    colWidths=[90 * mm, 90 * mm])
    code_t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(code_t2)
    story.append(Spacer(1, 6))

    # Сценарий 3
    story.append(Paragraph("📌 Сценарий 3: Генерация поста + Диффузия фото (generate_post)", h2_style))
    story.append(Paragraph("Сквозная генерация по матрице приоритетов с параллельным запуском моделей на GPU:", body_style))
    
    s3_req = (
        "{\n"
        '  "task_type": "generate_post",\n'
        '  "user_id": "usr_102", "brand_id": "brand_102",\n'
        '  "payload": {\n'
        '    "company_name": "Maison Cafe", "niche": "Кофейня",\n'
        '    "prompt": "хочу пост про кофе с собачкой",\n'
        '    "attachments": ["https://s3.ucust.ai/uploads/hands.png", "https://s3.ucust.ai/uploads/husky.png", "https://s3.ucust.ai/uploads/cafe.png"],\n'
        '    "options": {"generate_image": true, "aspect_ratio": "1:1"}\n'
        '  },\n'
        '  "sync_backend": true\n'
        "}"
    )
    s3_res = (
        "{\n"
        '  "status": "success", "task_type": "generate_post",\n'
        '  "data": {\n'
        '    "post_text": "Идеальное утро: любимый кофе, тепло рук и лучший четвероногий друг в «Maison Cafe» ☕🐶...",\n'
        '    "image_url": "https://s3.ucust.ai/output/photos/fused_scene_7721.png",\n'
        '    "hashtags": "#MaisonCafe #догфрендли #спешелтикофе",\n'
        '    "promo_code": "DOGCOFFEE15",\n'
        '    "timings": {"text_gen_seconds": 1.2, "photo_gen_seconds": 3.8, "total_seconds": 4.1}\n'
        '  }\n'
        "}"
    )
    code_t3 = Table([[Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ЗАПРОС БЭКЕНДА:</b><br/>{s3_req.replace(chr(10), '<br/>')}</font>", code_style),
                      Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ОТВЕТ AI:</b><br/>{s3_res.replace(chr(10), '<br/>')}</font>", code_style)]],
                    colWidths=[90 * mm, 90 * mm])
    code_t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(code_t3)

    story.append(PageBreak())

    # =============================================================
    # СТРАНИЦА 4: ПОДСИСТЕМА CLEAN RAG И СИНХРОНИЗАЦИЯ С SQL
    # =============================================================
    story.append(Paragraph("5. Синхронизация данных с базой (SQL / PostgreSQL + pgvector) и Clean RAG", h1_style))
    story.append(Paragraph(
        "База знаний брендов хранится в <b>PostgreSQL с расширением pgvector</b>. "
        "Подсистема <b>Clean RAG</b> обеспечивает защиту от галлюцинаций LLM, гарантируя, что цены, акции и факты о компании строго соответствуют загруженным данным.",
        body_style
    ))

    # Таблица структуры SQL
    sql_schema = (
        "-- Схема таблицы чанков базы знаний (Multi-Tenant pgvector)\n"
        "CREATE TABLE brand_knowledge_chunks (\n"
        "    id VARCHAR(64) PRIMARY KEY,\n"
        "    brand_id VARCHAR(64) NOT NULL,            -- Multi-Tenant изоляция бренда\n"
        "    doc_id VARCHAR(64) NOT NULL,\n"
        "    chunk_text TEXT NOT NULL,\n"
        "    category VARCHAR(32) DEFAULT 'general',    -- pricing | rules | promo | reviews\n"
        "    source VARCHAR(64) DEFAULT 'manual',       -- parser | docx | web | api\n"
        "    embedding vector(384) NOT NULL,            -- Векторные эмбеддинги MiniLM-L12\n"
        "    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\n"
        ");\n"
        "-- Высокоскоростной HNSW индекс векторного поиска по косинусному расстоянию (<=>)\n"
        "CREATE INDEX idx_chunks_vec ON brand_knowledge_chunks USING hnsw (embedding vector_cosine_ops);\n"
        "CREATE INDEX idx_chunks_brand ON brand_knowledge_chunks (brand_id);"
    )
    sql_table = Table([[Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>SQL СХЕМА ТАБЛИЦЫ PGVECTOR:</b><br/>{sql_schema.replace(chr(10), '<br/>')}</font>", code_style)]],
                      colWidths=[180 * mm])
    sql_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sql_table)
    story.append(Spacer(1, 6))

    # Сценарий rag_ingest и rag_query
    story.append(Paragraph("📌 Прямая индексация (rag_ingest) и поиск фактов (rag_query)", h2_style))
    
    rag_ingest_req = (
        "// POST /api/v1/orchestrator/execute\n"
        "{\n"
        '  "task_type": "rag_ingest",\n'
        '  "brand_id": "brand_102",\n'
        '  "payload": {\n'
        '    "documents": [\n'
        '      {\n'
        '        "doc_id": "price_2026",\n'
        '        "text": "Капучино на миндальном — 290р. Скидка со своей кружкой — 15%.",\n'
        '        "metadata": {"category": "pricing"}\n'
        '      },\n'
        '      {\n'
        '        "doc_id": "values",\n'
        '        "text": "Мы дог-френдли, на входе всегда есть миска со свежей водой.",\n'
        '        "metadata": {"category": "rules"}\n'
        '      }\n'
        '    ]\n'
        '  }\n'
        "}"
    )
    rag_query_req = (
        "// ПОИСК ПО БАЗЕ (rag_query):\n"
        "{\n"
        '  "task_type": "rag_query",\n'
        '  "brand_id": "brand_102",\n'
        '  "payload": {\n'
        '    "query": "какая скидка если прийти со своей кружкой?",\n'
        '    "top_k": 2\n'
        '  }\n'
        "}\n"
        "// ОТВЕТ AI (Score: 0.892):\n"
        "{\n"
        '  "has_sufficient_context": true,\n'
        '  "top_score": 0.892,\n'
        '  "context": "[ФАКТ] Скидка со своей кружкой — 15%. Капучино — 290р."\n'
        "}"
    )
    code_trag = Table([[Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>СОХРАНЕНИЕ В RAG (rag_ingest):</b><br/>{rag_ingest_req.replace(chr(10), '<br/>')}</font>", code_style),
                       Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ПОИСК ЗНАНИЙ (rag_query):</b><br/>{rag_query_req.replace(chr(10), '<br/>')}</font>", code_style)]],
                      colWidths=[90 * mm, 90 * mm])
    code_trag.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#f0fdf4')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(code_trag)
    story.append(Spacer(1, 6))

    # Конвейер Clean RAG шагов
    rag_steps = [
        [Paragraph("Этап", table_header_style), Paragraph("Компонент", table_header_style), Paragraph("Описание работы", table_header_style)],
        [
            Paragraph("<b>1. Чанкинг</b>", body_style),
            Paragraph("SemanticChunker", code_style),
            Paragraph("Нарезка документов на смысловые блоки по 350 токенов с перекрытием 50 токенов.", body_style)
        ],
        [
            Paragraph("<b>2. Векторизация</b>", body_style),
            Paragraph("SentenceTransformer", code_style),
            Paragraph("Быстрое локальное построение эмбеддингов <code>MiniLM-L12-v2</code> и сохранение в pgvector.", body_style)
        ],
        [
            Paragraph("<b>3. Поиск</b>", body_style),
            Paragraph("HybridRetriever", code_style),
            Paragraph("Комбинация ключевых слов (BM25) и семантического сходства (Cosine <=> в SQL) с фильтром <code>brand_id</code>.", body_style)
        ],
        [
            Paragraph("<b>4. Реранкинг</b>", body_style),
            Paragraph("CrossEncoderReranker", code_style),
            Paragraph("Перепроверка кандидатов через модель <code>BAAI/bge-reranker-base</code> для выбора топ-3 фактов.", body_style)
        ],
        [
            Paragraph("<b>5. Защита</b>", body_style),
            Paragraph("AntiHallucinationGuard", code_style),
            Paragraph("Если score < 0.55 — факт отбрасывается, LLM не выдумывает несуществующие цены и скидки.", body_style)
        ]
    ]
    rag_steps_t = Table(rag_steps, colWidths=[28 * mm, 42 * mm, 110 * mm])
    rag_steps_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(rag_steps_t)

    story.append(PageBreak())

    # =============================================================
    # СТРАНИЦА 5: БЕЗОПАСНОСТЬ, ПЕРЕДАЧА МЕДИА И CURL ШПАРГАЛКА
    # =============================================================
    story.append(Paragraph("6. Безопасность, передача медиа и Auto-Push Webhooks", h1_style))
    
    sec_items = [
        [
            Paragraph("<b>1. Защита от SSRF</b>", h2_style),
            Paragraph("Оркестратор валидирует все входящие URL-адреса. Запрещен доступ к localhost, 127.0.0.1, 10.0.x, 192.168.x и облачным метаданным (169.254.169.254).", body_style)
        ],
        [
            Paragraph("<b>2. Anti-Injection DLP</b>", h2_style),
            Paragraph("SecurityGuard фильтрует попытки взлома ('ignore previous instructions', 'dump database', 'select *'). Запросы немедленно блокируются со статусом error.", body_style)
        ],
        [
            Paragraph("<b>3. Передача медиа-файлов</b>", h2_style),
            Paragraph("Во избежание перегрузки сети Base64: Бэкенд передает URL файла в S3/MinIO. AI сохраняет баннер в хранилище и возвращает готовый <b>image_url</b>.", body_style)
        ],
        [
            Paragraph("<b>4. Фоновый Auto-Push</b>", h2_style),
            Paragraph("При флаге <b>sync_backend: true</b> оркестратор в неблокирующем режиме отправляет результат на Webhook Бэкенда <code>JAVA_BACKEND_CALLBACK_URL</code> с заголовком <code>X-Internal-Secret</code>.", body_style)
        ]
    ]
    sec_table = Table(sec_items, colWidths=[52 * mm, 128 * mm])
    sec_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sec_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # ШПАРГАЛКА ДЛЯ РАЗРАБОТЧИКА БЭКЕНДА
    # -------------------------------------------------------------
    story.append(Paragraph("7. Шпаргалка для разработчика Бэкенда (cURL / HTTP)", h1_style))
    
    curl_code = (
        "curl -X POST http://10.0.0.2:8000/api/v1/orchestrator/execute \\\n"
        "  -H 'Content-Type: application/json' \\\n"
        "  -H 'X-Internal-Secret: ucust-super-secret-service-token-2026' \\\n"
        "  -d '{\n"
        '    "task_type": "generate_post",\n'
        '    "user_id": "usr_992",\n'
        '    "brand_id": "brand_cafe_123",\n'
        '    "payload": {\n'
        '      "company_name": "Maison Cafe",\n'
        '      "prompt": "хочу пост про кофе с собачкой"\n'
        "    }\n"
        "  }'"
    )
    curl_table = Table([[Paragraph(f"<font face='ArialCustom' color='#0f172a'><b>ПРИМЕР ВЫЗОВА ЧЕРЕЗ CURL:</b><br/>{curl_code.replace(chr(10), '<br/>')}</font>", code_style)]],
                       colWidths=[180 * mm])
    curl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(curl_table)
    story.append(Spacer(1, 10))

    # Summary box
    summary_box = [
        [
            Paragraph(
                "<b>✅ Итог архитектуры:</b> Бэкенд полностью изолирован от деталей реализации AI (нод, моделей, весов). "
                "Все коммуникации стандартизированы через единый шлюз, поддерживают автоматический Auto-Push в БД, "
                "изоляцию данных multi-tenant в PostgreSQL + pgvector и гарантируют максимальную скорость отклика.",
                ParagraphStyle('SumBox', fontName='ArialCustom', fontSize=8.5, leading=12, textColor=colors.HexColor('#065f46'))
            )
        ]
    ]
    sum_table = Table(summary_box, colWidths=[180 * mm])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#10b981')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sum_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF successfully generated: {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "UCust_AI_Backend_Integration_Guide.pdf"
    create_pdf(out_file)
