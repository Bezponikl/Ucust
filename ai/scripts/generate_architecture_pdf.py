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
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='ArialCustom',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#475569'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'H1',
        fontName='ArialCustom-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        fontName='ArialCustom-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        fontName='ArialCustom',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='ArialCustom',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )

    badge_style = ParagraphStyle(
        'Badge',
        fontName='ArialCustom-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#ffffff')
    )

    story = []

    # -------------------------------------------------------------
    # HEADER BANNER
    # -------------------------------------------------------------
    banner_data = [
        [
            Paragraph("<b>UCust.AI Enterprise Engine</b>", ParagraphStyle('BTitle', fontName='ArialCustom-Bold', fontSize=14, leading=17, textColor=colors.HexColor('#ffffff'))),
            Paragraph("<b>Архитектура 2026</b>", ParagraphStyle('BSub', fontName='ArialCustom-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#93c5fd'), alignment=2))
        ],
        [
            Paragraph("<b>ЕДИНОЕ РУКОВОДСТВО ПО ИНТЕГРАЦИИ БЭКЕНДА С AI-ОРКЕСТРАТОРОМ</b><br/><font size='8' color='#cbd5e1'>Протокол межсерверного взаимодействия (Сервер 1: Бэкенд / Сервер 2: AI GPU Node)</font>", ParagraphStyle('BDesc', fontName='ArialCustom', fontSize=10, leading=13, textColor=colors.HexColor('#ffffff'))),
            ""
        ]
    ]
    banner_table = Table(banner_data, colWidths=[130 * mm, 50 * mm])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('SPAN', (0, 1), (1, 1)),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 1. ОБЗОР И ПРИНЦИП ЕДИНОГО ШЛЮЗА
    # -------------------------------------------------------------
    story.append(Paragraph("1. Архитектурная концепция Единого Шлюза (Unified Task Gateway)", h1_style))
    story.append(Paragraph(
        "В системе UCust реализован паттерн <b>Unified Command Gateway</b>. Основной Бэкенд (Java / Node.js) взаимодействует "
        "с AI GPU-нодой через <b>ровно один защищенный эндпоинт</b>. Все микросервисы (парсинг сайтов, соцсетей, карт, "
        "компьютерное зрение Moondream VLM, генерация текстов Saiga и диффузия изображений ComfyUI) оркестрируются внутри AI-ядра.",
        body_style
    ))

    # Таблица сетевых параметров
    net_data = [
        [Paragraph("<b>Параметр</b>", body_style), Paragraph("<b>Значение в .env</b>", body_style), Paragraph("<b>Назначение</b>", body_style)],
        [Paragraph("<b>Эндпоинт шлюза</b>", body_style), Paragraph("<font color='#1d4ed8'>POST http://10.0.0.2:8000/api/v1/orchestrator/execute</font>", code_style), Paragraph("Единый адрес приема задач от Бэкенда", body_style)],
        [Paragraph("<b>Алиас шлюза</b>", body_style), Paragraph("<font color='#1d4ed8'>POST http://10.0.0.2:8000/api/v1/task/execute</font>", code_style), Paragraph("Альтернативный короткий адрес", body_style)],
        [Paragraph("<b>Заголовок авторизации</b>", body_style), Paragraph("<b>X-Internal-Secret</b>: ucust-super-secret-service-token-2026", code_style), Paragraph("Секретный токен приватной сети WireGuard", body_style)],
        [Paragraph("<b>Webhook Бэкенда (Посты)</b>", body_style), Paragraph("JAVA_BACKEND_CALLBACK_URL=http://10.0.0.1:8080/api/v1/ai/callback", code_style), Paragraph("Куда AI пушит готовые посты, фото и видео", body_style)],
        [Paragraph("<b>Webhook Бэкенда (Данные)</b>", body_style), Paragraph("BACKEND_COLLECTOR_CALLBACK_URL=http://10.0.0.1:8080/api/v1/collectors/sync", code_style), Paragraph("Куда AI пушит результаты парсинга и анкеты", body_style)],
    ]
    net_table = Table(net_data, colWidths=[40 * mm, 80 * mm, 60 * mm])
    net_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(net_table)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------
    # 2. МАТРИЦА ЗАДАЧ (TASK_TYPE)
    # -------------------------------------------------------------
    story.append(Paragraph("2. Сводная матрица задач (Все поддерживаемые task_type)", h1_style))
    
    tasks_data = [
        [Paragraph("<b>task_type</b>", body_style), Paragraph("<b>Что выполняет AI-ядро</b>", body_style), Paragraph("<b>Когда вызывать</b>", body_style), Paragraph("<b>Среднее время</b>", body_style)],
        [
            Paragraph("<b>quick_vision</b>", ParagraphStyle('T1', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Moondream VLM распознает фото, извлекает HEX-палитру, определяет ноды 55/64/65 воркфлоу realism2.0 и кэширует fusion-промпт.", body_style),
            Paragraph("<b>Сразу при загрузке 1-3 фото</b> на фронте.", body_style),
            Paragraph("<b>< 0.5 сек</b>", body_style)
        ],
        [
            Paragraph("<b>analyze_documents</b>", ParagraphStyle('T2', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("DocumentCollector парсит PDF, DOCX, PPTX (прайсы, КП), извлекает таблицы и индексирует в Clean RAG память бренда.", body_style),
            Paragraph("При загрузке файлов клиентом в анкету.", body_style),
            Paragraph("<b>0.3 - 1.0 сек</b>", body_style)
        ],
        [
            Paragraph("<b>quick_scan</b>", ParagraphStyle('T3', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Параллельный быстрый парсинг сайта, VK, 2GIS/Яндекс для моментального извлечения названия, лого, цветов, УТП и отзывов.", body_style),
            Paragraph("При вводе ссылок на шаге 1 анкеты.", body_style),
            Paragraph("<b>0.4 - 0.8 сек</b>", body_style)
        ],
        [
            Paragraph("<b>onboard_user</b>", ParagraphStyle('T4', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Комплексный анализ профиля, составление контент-стратегии 3x3, ЦА, SWOT, тональности и полной базы RAG.", body_style),
            Paragraph("При завершении регистрации/онбординга.", body_style),
            Paragraph("<b>1.5 - 3.0 сек</b>", body_style)
        ],
        [
            Paragraph("<b>generate_post</b>", ParagraphStyle('T5', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#059669'))),
            Paragraph("Сквозной синтез: Saiga LLM (текст по Хант-матрице) ⨂ ComfyUI Diffuse (реалистичный кадр realism2.0) + Критик.", body_style),
            Paragraph("По кнопке «Создать пост» / по расписанию.", body_style),
            Paragraph("<b>2.0 - 5.5 сек</b>", body_style)
        ],
        [
            Paragraph("<b>plan_content</b>", ParagraphStyle('T6', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("ContentStrategyEngine формирует календарь постов на N дней с учетом праздников, болей аудитории и сетки 3x3.", body_style),
            Paragraph("При запросе контент-плана на неделю/месяц.", body_style),
            Paragraph("<b>0.8 - 1.5 сек</b>", body_style)
        ],
        [
            Paragraph("<b>get_graph_data</b>", ParagraphStyle('T7', fontName='ArialCustom-Bold', fontSize=8, textColor=colors.HexColor('#2563eb'))),
            Paragraph("Security DLP: отдает очищенные от PII данные для графиков и дашбордов статистики в интерфейсе.", body_style),
            Paragraph("При открытии страницы аналитики.", body_style),
            Paragraph("<b>< 0.1 сек</b>", body_style)
        ],
    ]
    tasks_table = Table(tasks_data, colWidths=[33 * mm, 80 * mm, 45 * mm, 22 * mm])
    tasks_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(tasks_table)
    
    story.append(PageBreak())

    # -------------------------------------------------------------
    # 3. ПОШАГОВЫЕ ПРИМЕРЫ ЗАПРОСОВ И ОТВЕТОВ
    # -------------------------------------------------------------
    story.append(Paragraph("3. Пошаговые сценарии и контракты данных (JSON DTO)", h1_style))

    # Сценарий 1
    story.append(Paragraph("📌 Сценарий 1: Быстрый скан ссылок при вводе в анкету (Шаг 1)", h2_style))
    story.append(Paragraph("Бэкенд отправляет запрос на шлюз сразу при вставке ссылки пользователем:", body_style))
    
    s1_req = (
        "// POST http://10.0.0.2:8000/api/v1/orchestrator/execute\n"
        "{\n"
        '  "task_type": "quick_scan",\n'
        '  "user_id": "usr_102",\n'
        '  "payload": {\n'
        '    "urls": ["https://maisoncafe.ru", "https://vk.com/maison_cafe", "https://2gis.ru/firm/7000000102"],\n'
        '    "city": "Москва"\n'
        '  },\n'
        '  "sync_backend": false\n'
        "}"
    )
    s1_res = (
        "// ОТВЕТ ОРКЕСТРАТОРА (JSON):\n"
        "{\n"
        '  "status": "success", "task_type": "quick_scan", "user_id": "usr_102",\n'
        '  "data": {\n'
        '    "prefilled_profile": {\n'
        '      "business_name": "Maison Cafe",\n'
        '      "niche": "Крафтовая кофейня и авторская кондитерская",\n'
        '      "brand_colors": ["#8B5A2B", "#D2B48C", "#FFF8DC"],\n'
        '      "description": "Спешелти кофе свежей обжарки, завтраки весь день.",\n'
        '      "contacts": {"phone": "+7 (495) 000-00-00", "address": "ул. Арбат, 10"},\n'
        '      "reviews_summary": "Рейтинг 4.9. Хвалят авторский капучино и уютную атмосферу."\n'
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(code_t1)
    story.append(Spacer(1, 8))

    # Сценарий 2
    story.append(Paragraph("📌 Сценарий 2: Моментальный анализ фото при загрузке (Moondream Pre-Analysis)", h2_style))
    story.append(Paragraph("Отправляется в момент прикрепления фото пользователем, чтобы не ждать при генерации поста:", body_style))
    
    s2_req = (
        "{\n"
        '  "task_type": "quick_vision",\n'
        '  "user_id": "usr_102",\n'
        '  "payload": {\n'
        '    "prompt": "хочу чтобы на таких руках сидела эта собачка и мы пили кофе в этой кофейне",\n'
        '    "attachments": [\n'
        '      "https://s3.ucust.ai/uploads/hands.png",\n'
        '      "https://s3.ucust.ai/uploads/husky.png",\n'
        '      "https://s3.ucust.ai/uploads/cafe.png"\n'
        '    ]\n'
        '  }\n'
        "}"
    )
    s2_res = (
        "{\n"
        '  "status": "success", "task_type": "quick_vision",\n'
        '  "data": {\n'
        '    "brand_colors": ["#8B5A2B", "#D2B48C", "#E8ECEF"],\n'
        '    "slot_mapping": {\n'
        '      "image1_node55": {"label": "Руки с маникюром в свитере", "role": "hands_body"},\n'
        '      "image2_node64": {"label": "Собака породы хаски", "role": "pet_animal"},\n'
        '      "image3_node65": {"label": "Интерьер кофейни с чашкой кофе", "role": "environment"}\n'
        '    },\n'
        '    "visual_narrative": "Объединенная сцена: девушка с нежным маникюром держит собачку..."\n'
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(code_t2)
    story.append(Spacer(1, 8))

    # Сценарий 3
    story.append(Paragraph("📌 Сценарий 3: Генерация готового поста + Диффузия фото (ComfyUI + Saiga)", h2_style))
    story.append(Paragraph("Сквозная генерация по матрице приоритетов с параллельным запуском моделей на GPU:", body_style))
    
    s3_req = (
        "{\n"
        '  "task_type": "generate_post",\n'
        '  "user_id": "usr_102",\n'
        '  "session_id": "post_job_7721",\n'
        '  "payload": {\n'
        '    "company_name": "Maison Cafe", "niche": "Кофейня", "city": "Москва",\n'
        '    "prompt": "хочу чтобы на таких руках сидела эта собачка и мы пили кофе в этой кофейне",\n'
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
        '    "post_text": "Идеальное утро: любимый кофе, тепло рук и лучший четвероногий друг в «Maison Cafe» ☕🐶\\n\\nЕсть мгновения, в которых идеально всё: мягкий трикотаж любимого свитера, аккуратный свежий маникюр, чашка согревающего капучино с нежной пенкой...",\n'
        '    "image_url": "https://s3.ucust.ai/output/photos/fused_scene_7721.png",\n'
        '    "hashtags": "#MaisonCafe #кофемосква #догфрендли #спешелтикофе",\n'
        '    "promo_code": "DOGCOFFEE15",\n'
        '    "timings": {"text_gen_seconds": 1.2, "photo_gen_seconds": 4.5, "total_seconds": 4.8}\n'
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
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(code_t3)

    story.append(PageBreak())

    # -------------------------------------------------------------
    # 4. БЕЗОПАСНОСТЬ, ХРАНЕНИЕ МЕДИА И BEST PRACTICES
    # -------------------------------------------------------------
    story.append(Paragraph("4. Безопасность, передача медиа и Auto-Push Webhooks", h1_style))
    
    sec_items = [
        [
            Paragraph("<b>1. Защита от SSRF</b>", h2_style),
            Paragraph("Оркестратор автоматически валидирует любые входящие URL-адреса. Запрещен доступ к локальным адресам (localhost, 127.0.0.1) и приватным диапазонам (10.0.0.0/8, 192.168.0.0/16, 169.254.169.254).", body_style)
        ],
        [
            Paragraph("<b>2. Защита от инъекций</b>", h2_style),
            Paragraph("SecurityGuard фильтрует попытки взлома ('ignore previous instructions', 'dump database', 'select *'). Такие запросы немедленно отклоняются со статусом 'error'.", body_style)
        ],
        [
            Paragraph("<b>3. Передача медиа-файлов</b>", h2_style),
            Paragraph("Чтобы избежать перегрузки сетевого канала передачей больших Base64-строк: Бэкенд передает URL файла в S3/MinIO или путь к общему диску. AI сохраняет баннер в хранилище и возвращает готовый <b>image_url</b>.", body_style)
        ],
        [
            Paragraph("<b>4. Фоновый Auto-Push</b>", h2_style),
            Paragraph("При флаге <b>sync_backend: true</b> оркестратор в неблокирующем фоновом режиме (asyncio task) отправляет готовый результат на Webhook Бэкенда <code>JAVA_BACKEND_CALLBACK_URL</code> с заголовком <code>X-Internal-Secret</code>.", body_style)
        ]
    ]
    sec_table = Table(sec_items, colWidths=[55 * mm, 125 * mm])
    sec_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sec_table)
    story.append(Spacer(1, 14))

    # -------------------------------------------------------------
    # 5. ШПАРГАЛКА ДЛЯ РАЗРАБОТЧИКА БЭКЕНДА (CHEATSHEET)
    # -------------------------------------------------------------
    story.append(Paragraph("5. Шпаргалка для разработчика Бэкенда (cURL / Java / TypeScript)", h1_style))
    
    curl_code = (
        "curl -X POST http://10.0.0.2:8000/api/v1/orchestrator/execute \\\n"
        "  -H 'Content-Type: application/json' \\\n"
        "  -H 'X-Internal-Secret: ucust-super-secret-service-token-2026' \\\n"
        "  -d '{\n"
        '    "task_type": "generate_post",\n'
        '    "user_id": "usr_992",\n'
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
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(curl_table)
    story.append(Spacer(1, 12))

    # Summary box
    summary_box = [
        [
            Paragraph(
                "<b>✅ Итог архитектуры:</b> Бэкенд полностью изолирован от деталей реализации AI (нод, моделей, весов). "
                "Все коммуникации стандартизированы через единый шлюз, поддерживают автоматический Auto-Push в БД и гарантируют максимальную скорость.",
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
