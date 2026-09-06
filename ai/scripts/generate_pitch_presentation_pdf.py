# File: ai/scripts/generate_pitch_presentation_pdf.py
"""
Executive Pitch Deck, Architecture Presentation & Cheat-Sheet for UCust.AI.
Генерирует полноцветный, презентационный PDF-документ альбомного / презентационного формата
со всеми точными схемами, воронками TOFU/MOFU/BOFU, формулами метрик,
пайплайном парсеров, VLM Moondream2, воркфлоу Realism 2.0 и шпаргалкой для питча.
"""

import os
import sys
import shutil

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PitchDeckNumberedCanvas(canvas.Canvas):
    """Презентационный канвас с фирменным стилем UCust, нумерацией слайдов и колонтитулами."""
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
            self.draw_slide_decorations(page_count)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, page_count: int):
        self.saveState()
        
        # Размеры страницы (Альбомный A4: 297mm x 210mm)
        page_w, page_h = landscape(A4)

        if self._pageNumber > 1:
            # Верхний баннер
            self.setFont("Arial-Bold", 8)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(1.2 * cm, page_h - 1.0 * cm, "UCUST.AI")
            
            self.setFont("Arial", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(3.2 * cm, page_h - 1.0 * cm, "•   Executive Presentation & Pitch Cheat-Sheet   •   Autonomous Multi-Agent MarTech Engine")
            
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.75)
            self.line(1.2 * cm, page_h - 1.15 * cm, page_w - 1.2 * cm, page_h - 1.15 * cm)

            # Нижний футер
            self.line(1.2 * cm, 1.1 * cm, page_w - 1.2 * cm, 1.1 * cm)
            self.setFont("Arial", 7.5)
            self.setFillColor(colors.HexColor("#94A3B8"))
            self.drawString(1.2 * cm, 0.7 * cm, "Конфиденциально • Разработано для UCust Enterprise Ecosystem • Версия 2.4.0 (Realism 2.0 Unified)")
            
            page_str = f"Слайд {self._pageNumber} из {page_count}"
            self.drawRightString(page_w - 1.2 * cm, 0.7 * cm, page_str)

        self.restoreState()


def generate_pitch_deck_pdf():
    # Регистрация системных шрифтов
    font_path = "C:/Windows/Fonts/arial.ttf"
    font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    pdfmetrics.registerFont(TTFont("Arial", font_path))
    pdfmetrics.registerFont(TTFont("Arial-Bold", font_bold_path))

    ai_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = os.path.dirname(ai_dir)
    output_dir = os.path.join(ai_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_filename_out = os.path.join(output_dir, "UCust_AI_Readiness_Audit_and_Roadmap.pdf")
    pdf_filename_root = os.path.join(root_dir, "UCust_AI_Readiness_Audit_and_Roadmap.pdf")

    page_w, page_h = landscape(A4)
    doc = SimpleDocTemplate(
        pdf_filename_out,
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.3 * cm
    )

    styles = getSampleStyleSheet()

    # Стили текста презентации
    s_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    s_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#3B82F6"),
        spaceAfter=15
    )
    s_h1 = ParagraphStyle(
        "SlideHeader",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=16,
        leading=19,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=8
    )
    s_h2 = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    s_body = ParagraphStyle(
        "SlideBody",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )
    s_body_bold = ParagraphStyle(
        "SlideBodyBold",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0F172A")
    )
    s_code = ParagraphStyle(
        "SlideCode",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0369A1")
    )
    s_alert = ParagraphStyle(
        "SlideAlert",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#B91C1C")
    )
    s_table_hdr = ParagraphStyle(
        "TableHdr",
        parent=styles["Normal"],
        fontName="Arial-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    )
    s_table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#1E293B")
    )

    story = []

    # =========================================================================
    # СЛАЙД 1: ТИТУЛЬНЫЙ ЛИСТ / EXECUTIVE OVERVIEW & PITCH HOOK
    # =========================================================================
    story.append(Spacer(1, 1.2 * cm))
    
    badge_table = Table(
        [[Paragraph("<b>ENTERPRISE AI MARTECH ECOSYSTEM</b>", ParagraphStyle("B", fontName="Arial-Bold", fontSize=8, textColor=colors.HexColor("#2563EB")))]],
        colWidths=[7.0 * cm]
    )
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#BFDBFE")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("UCUST.AI — Автономная мультиагентная SMM-экосистема", s_title))
    story.append(Paragraph("Сквозная архитектура: Парсеры • Moondream2 VLM • Сайга LLM • Умные Воронки • Realism 2.0 ComfyUI", s_subtitle))
    
    pitch_card_data = [
        [
            Paragraph("<b>🎯 Главная ценность для бизнеса / Инвестора:</b><br/>"
                      "Замена целого SMM-отдела (Аналитик + Сценарист + Дизайнер + Таргетолог) на <b>автономный 4-уровневый конвейер</b>, "
                      "который за <b>8 секунд</b> собирает аналитику конкурентов, выстраивает сетку 3x3, создает конвертирующий текст по 3 ступеням воронки (TOFU/MOFU/BOFU) "
                      "и рендерит фотореалистичный кадр по стандартам iPhone 16 Pro (без студийного пластика).", s_body)
        ]
    ]
    pitch_card = Table(pitch_card_data, colWidths=[26.5 * cm])
    pitch_card.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(pitch_card)
    story.append(Spacer(1, 0.6 * cm))

    metrics_row = [
        [
            Paragraph("<b>⏱️ Скорость генерации</b><br/><font size=14 color='#2563EB'><b>6-8 сек</b></font><br/>Полный цикл с визулом", s_body),
            Paragraph("<b>🛡️ Изоляция RAG</b><br/><font size=14 color='#10B981'><b>100%</b></font><br/>0% утечек между клиентами", s_body),
            Paragraph("<b>🚫 Защита от бреда</b><br/><font size=14 color='#8B5CF6'><b>CriticMunger</b></font><br/>1 мс Regex Gatekeeper", s_body),
            Paragraph("<b>📸 Стандарт визуала</b><br/><font size=14 color='#EA580C'><b>Realism 2.0</b></font><br/>26-нодовый T2I/I2I граф", s_body)
        ]
    ]
    t_metrics = Table(metrics_row, colWidths=[6.5 * cm, 6.5 * cm, 6.5 * cm, 6.5 * cm])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_metrics)
    story.append(PageBreak())

    # =========================================================================
    # СЛАЙД 2: СТРУКТУРА МУЛЬТИАГЕНТНОЙ ЭКОСИСТЕМЫ (4 УРОВНЯ)
    # =========================================================================
    story.append(Paragraph("1. Архитектурный каркас экосистемы (4-Tier Infrastructure)", s_h1))
    story.append(Paragraph("Четкое разделение зон ответственности исключает перегрузку VRAM и гарантирует отказоустойчивость.", s_subtitle))

    col1 = Paragraph(
        "<b>УРОВЕНЬ 1: Сбор и Парсинг (Ingestion)</b><br/>"
        "• <b>Telethon Collector (MTProto):</b> Глубокий сбор истории, комментариев и реакций.<br/>"
        "• <b>Web Preview Scraper:</b> Мгновенный Zero-Auth доступ к открытым каналам (<code>t.me/s/</code>).<br/>"
        "• <b>VK API & 2ГИС:</b> Сбор гео-отзывов и инфоповодов конкурентов.<br/>"
        "• <i>Железо:</i> 100% CPU / Async I/O (0 МБ VRAM).<br/><br/>"
        "<b>УРОВЕНЬ 2: Мультимодальный анализ (Vision & RAG)</b><br/>"
        "• <b>Moondream2 VLM:</b> Анализ геометрии, света, контраста и извлечение Hex-палитры.<br/>"
        "• <b>Hybrid RAG:</b> Векторный MiniLM-L12-v2 + BM25 с изоляцией по <code>tenant_id</code>.<br/>"
        "• <b>MediaUtils CV:</b> Мгновенный фолбэк-квантизатор палитры (15 мс на CPU).",
        s_body
    )

    col2 = Paragraph(
        "<b>УРОВЕНЬ 3: Мозг и Арбитраж (Brain & Gatekeeper)</b><br/>"
        "• <b>ContextRouter (4 квадранта):</b> B2B_TECH, B2B_SERVICE, B2C_ECOM, B2C_LIFESTYLE.<br/>"
        "• <b>Bridge Mode:</b> Гармоничное скрещивание тем (IT + Котики/Кофе) без потери ДНК бренда.<br/>"
        "• <b>Сайга LLM (Llama-3-8B):</b> Генерация по фреймворкам BAB, PAS, AIDA, StoryBrand.<br/>"
        "• <b>CriticMunger:</b> 1 мс Regex Gatekeeper против B2B-оксюморонов и штампов.<br/><br/>"
        "<b>УРОВЕНЬ 4: Рендеринг визуала (Realism 2.0 Engine)</b><br/>"
        "• <b>ComfyUI Headless (26 нод):</b> Аппаратный свитч (Нода 72/73) между T2I и I2I.<br/>"
        "• <b>FluxKontext Multi-Reference:</b> Сохранение лица амбассадора и геометрии товара.<br/>"
        "• <b>Color Guard:</b> Инжекция 5 Hex-цветов бренда в позитивный промпт.",
        s_body
    )

    t_tiers = Table([[col1, col2]], colWidths=[13.0 * cm, 13.0 * cm])
    t_tiers.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_tiers)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("<b>Ключевое преимущество для питча:</b> Архитектура Payload-Driven переносит 80% тяжести на дешевый этап пре-роутинга (CPU), делая вызов тяжелых нейросетей точечным и безошибочным.", s_code))
    story.append(PageBreak())

    # =========================================================================
    # СЛАЙД 3: ПАРСЕРЫ, ТЕЛЕМЕТРИЯ И ФОРМУЛА ENGAGEMENT SCORE
    # =========================================================================
    story.append(Paragraph("2. Парсеры, Moondream2 и Формула телеметрии вовлеченности", s_h1))
    story.append(Paragraph("Сквозной сбор реальных данных вместо слепого угадывания интересов аудитории.", s_subtitle))

    formula_text = Paragraph(
        "<b>Математическая модель скоринга эффективности постов (Feedback Telemetry):</b><br/>"
        "<font size=12 color='#1E3A8A'><b>Score = (w₁ · pLike) + (w₂ · pShare) + (w₃ · pWatch) - (w₄ · pSkip)</b></font><br/>"
        "• <b>pShare (Репосты):</b> Максимальный вес для органического роста охватов (TOFU).<br/>"
        "• <b>pLike (Одобрение):</b> Базовый маркер согласия с ценностями и тезисами.<br/>"
        "• <b>pWatch (Глубина чтения):</b> Удержание внимания на экспертных лонгридах (MOFU).<br/>"
        "• <b>pSkip (Штрафной вес):</b> Фиксация пролистываний и скрытий. При росте pSkip система снижает агрессивность рекламы.",
        s_body
    )
    
    t_form = Table([[formula_text]], colWidths=[26.5 * cm])
    t_form.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#FDE68A")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_form)
    story.append(Spacer(1, 0.4 * cm))

    # Таблица парсеров
    p_data = [
        [
            Paragraph("<b>Протокол</b>", s_table_hdr),
            Paragraph("<b>Назначение и Глубина</b>", s_table_hdr),
            Paragraph("<b>Скорость</b>", s_table_hdr),
            Paragraph("<b>Связка с VLM Moondream2</b>", s_table_hdr)
        ],
        [
            Paragraph("<b>Telethon (MTProto)</b>", s_table_cell),
            Paragraph("Полная история каналов, реакции, комментарии, закрытые группы", s_table_cell),
            Paragraph("1.5–3 сек", s_table_cell),
            Paragraph("Скачивание HD-оригиналов (до 2 ГБ) напрямую из Telegram DC", s_table_cell)
        ],
        [
            Paragraph("<b>Web Scraper (t.me/s/)</b>", s_table_cell),
            Paragraph("Экспресс-аудит открытых каналов (Zero-Auth, 0 ключей, 0 риска бана)", s_table_cell),
            Paragraph("150–300 мс", s_table_cell),
            Paragraph("Сбор превью последних 9 постов для мгновенной сетки 3x3", s_table_cell)
        ],
        [
            Paragraph("<b>VK API & 2ГИС</b>", s_table_cell),
            Paragraph("Сбор постов на стене, отзывов клиентов, локальных гео-трендов", s_table_cell),
            Paragraph("200–500 мс", s_table_cell),
            Paragraph("Анализ фотографий посетителей для выявления реальной палитры", s_table_cell)
        ]
    ]
    t_par = Table(p_data, colWidths=[4.5 * cm, 9.5 * cm, 3.5 * cm, 9.0 * cm])
    t_par.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_par)
    story.append(PageBreak())

    # =========================================================================
    # СЛАЙД 4: ВОРОНКИ ПРОДАЖ (TOFU / MOFU / BOFU) И АРБИТРАЖ ИНТЕНТА
    # =========================================================================
    story.append(Paragraph("3. Маркетинговые воронки (TOFU / MOFU / BOFU) и Авто-Арбитраж", s_h1))
    story.append(Paragraph("Система автоматически балансирует ленту по правилу 50/30/20, исключая выгорание базы.", s_subtitle))

    f_data = [
        [
            Paragraph("<b>Этап воронки</b>", s_table_hdr),
            Paragraph("<b>Бизнес-цель</b>", s_table_hdr),
            Paragraph("<b>Психологический фреймворк</b>", s_table_hdr),
            Paragraph("<b>Правило CTA & Мемов</b>", s_table_hdr),
            Paragraph("<b>Стиль визуала (Realism 2.0)</b>", s_table_hdr)
        ],
        [
            Paragraph("<b>TOFU</b><br/>(Верх воронки)", s_table_cell),
            Paragraph("Привлечение холодного трафика, разрушение мифов, вирусные охваты", s_table_cell),
            Paragraph("<b>BAB</b> (Before - After - Bridge)<br/><b>StoryBrand</b> (Герой/Проводник)", s_table_cell),
            Paragraph("🔥 Мемы: <b>РАЗРЕШЕНЫ</b><br/>CTA: «Перешли / Напиши мнение»<br/>⛔ Запрет жестких продаж", s_table_cell),
            Paragraph("Живое UGC-фото на iPhone 16 Pro (24mm), естественный свет, эмоции", s_table_cell)
        ],
        [
            Paragraph("<b>MOFU</b><br/>(Середина)", s_table_cell),
            Paragraph("Прогрев, экспертное обоснование, демонстрация технологии, кейсы", s_table_cell),
            Paragraph("<b>PAS</b> (Problem - Agitation - Solution)<br/>Архитектурные разборы", s_table_cell),
            Paragraph("⚖️ Мемы: Ограничены<br/>CTA: «Сохрани / Задай вопрос»<br/>Умеренные метрики", s_table_cell),
            Paragraph("Процесс работы, макро-детали интерфейса, бэкстейдж команды", s_table_cell)
        ],
        [
            Paragraph("<b>BOFU</b><br/>(Низ воронки)", s_table_cell),
            Paragraph("Конверсия в регистрацию, закрытие в сделку, продажа спецпредложения", s_table_cell),
            Paragraph("<b>AIDA</b> (Attention-Interest-Desire-Action)<br/><b>FAB</b> (Свойства-Преимущества)", s_table_cell),
            Paragraph("⛔ Мемы: <b>СТРОГО ЗАПРЕЩЕНЫ</b><br/>CTA: «Купи / Оставь заявку»<br/>Четкий дедлайн и скидка", s_table_cell),
            Paragraph("Фокус на продукте крупным планом, контрастный бренд-акцент", s_table_cell)
        ]
    ]
    t_fun = Table(f_data, colWidths=[3.5 * cm, 6.5 * cm, 5.5 * cm, 5.5 * cm, 5.5 * cm])
    t_fun.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#EFF6FF")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#FEF2F2")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_fun)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(
        "<b>Детектор усталости (Audience Fatigue Lock):</b> Если в канале вышло 2 продающих поста подряд (BOFU), "
        "система принудительно сбрасывает следующий слот в TOFU (Охват/Юмор), защищая канал от массовых отписок.",
        s_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # СЛАЙД 5: UNIFIED REALISM 2.0 & ПРОМПТ-ИНЖИНИРИНГ ВИЗУАЛА
    # =========================================================================
    story.append(Paragraph("4. Единый воркфлоу генерации Realism 2.0 (ComfyUI Headless)", s_h1))
    story.append(Paragraph("26-нодовый граф объединяет Text-to-Image и Multi-Reference Image Editing без переключения файлов.", s_subtitle))

    v_col1 = Paragraph(
        "<b>Аппаратный переключатель (Ноды 72 & 73):</b><br/>"
        "• <b>Node 72 (PrimitiveBoolean Mode: Edit):</b> Автоматически выставляет <code>False</code> (генерация с нуля из шума) или <code>True</code> (редактирование по референсам).<br/>"
        "• <b>Node 73 (Latent Input Switch):</b> Направляет в KSampler либо пустой латент (Node 74), либо закодированные референсы (Node 58).<br/><br/>"
        "<b>Сохранение Бренда (Multi-Reference):</b><br/>"
        "• <b>Nodes 55, 64, 65 (LoadImage):</b> Слоты под Фото 1 (Товар/Лицо), Фото 2 (Локация), Фото 3 (Стиль).<br/>"
        "• <b>Nodes 62, 63 (FluxKontext):</b> 100% консистентность физических черт продукта при смене фона.",
        s_body
    )

    v_col2 = Paragraph(
        "<b>Формула мобильного реализма (UGC Standard):</b><br/>"
        "• <b>Оптика:</b> <code>shot on iPhone 16 Pro, 24mm main camera, eye-level handheld</code>.<br/>"
        "• <b>Освещение:</b> <code>natural ambient window daylight, realistic room shadows</code>.<br/>"
        "• <b>Color Guard:</b> Авто-инжекция 5 Hex-цветов из брендбука.<br/><br/>"
        "<b>Жесткие негативные фильтры (Anti-Plastic):</b><br/>"
        "<code>staged studio photoshoot, heavy artificial studio strobes, plastic skin, airbrushed, wax figure, 3d render, cgi, cartoon, overly smooth, fake lighting</code>",
        s_body
    )

    t_v = Table([[v_col1, v_col2]], colWidths=[13.0 * cm, 13.0 * cm])
    t_v.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_v)
    story.append(Spacer(1, 0.4 * cm))

    # Сетка 3x3
    grid_data = [
        [
            Paragraph("<b>#1 Эмоции/Люди</b><br/>Человек в естеств. свете", s_table_cell),
            Paragraph("<b>#2 Макро-Деталь</b><br/>Фокус на товаре/текстуре", s_table_cell),
            Paragraph("<b>#3 Пространство</b><br/>Локация, интерьер, город", s_table_cell)
        ],
        [
            Paragraph("<b>#4 Действие</b><br/>Динамичный процесс работы", s_table_cell),
            Paragraph("<b>#5 Главный Акцент</b><br/>Контрастный оффер / УТП", s_table_cell),
            Paragraph("<b>#6 Детали/Артефакты</b><br/>Инструменты, материалы", s_table_cell)
        ],
        [
            Paragraph("<b>#7 Закулисье</b><br/>Бэкстейдж подготовки", s_table_cell),
            Paragraph("<b>#8 Соц. Пруф</b><br/>Результат «До/После»", s_table_cell),
            Paragraph("<b>#9 Воздух/Минимализм</b><br/>Эстетическая разгрузка", s_table_cell)
        ]
    ]
    t_grid = Table(grid_data, colWidths=[8.8 * cm, 8.8 * cm, 8.8 * cm])
    t_grid.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#94A3B8")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(Paragraph("<b>Матрица композиционного ритма 3x3 (Grid DNA Planning Matrix):</b>", s_h2))
    story.append(t_grid)
    story.append(PageBreak())

    # =========================================================================
    # СЛАЙД 6: АППАРАТНОЕ РАСПРЕДЕЛЕНИЕ РЕСУРСОВ (CPU vs GPU TIME-DIVISION)
    # =========================================================================
    story.append(Paragraph("5. Аппаратная экономика и работа при высоком наплыве (High-Load)", s_h1))
    story.append(Paragraph("Как система обслуживает сотни клиентов на ограниченном пуле GPU без падений по OOM.", s_subtitle))

    hw_data = [
        [
            Paragraph("<b>Компонент</b>", s_table_hdr),
            Paragraph("<b>Устройство</b>", s_table_hdr),
            Paragraph("<b>Потребление памяти</b>", s_table_hdr),
            Paragraph("<b>Роль и Приоритет</b>", s_table_hdr)
        ],
        [
            Paragraph("<b>Парсеры (Telethon, VK, 2ГИС)</b>", s_table_cell),
            Paragraph("⚙️ <b>CPU</b> (Многопоточность)", s_table_cell),
            Paragraph("50–100 МБ RAM (0 МБ VRAM)", s_table_cell),
            Paragraph("Фоновый приоритет (Below Normal). Сетевой асинхронный I/O", s_table_cell)
        ],
        [
            Paragraph("<b>RAG Поиск (MiniLM + BM25)</b>", s_table_cell),
            Paragraph("⚙️ <b>CPU</b> (384-dim энкодер)", s_table_cell),
            Paragraph("~150 МБ RAM (0 МБ VRAM)", s_table_cell),
            Paragraph("Нормальный. Поиск чанков за 10–20 мс без загрузки в видеокарту", s_table_cell)
        ],
        [
            Paragraph("<b>ContextRouter & CriticMunger</b>", s_table_cell),
            Paragraph("⚙️ <b>CPU</b> (Regex / Heuristics)", s_table_cell),
            Paragraph("< 20 МБ RAM (0 МБ VRAM)", s_table_cell),
            Paragraph("Мгновенный (1 мс). Отсечение B2B-оксюморонов до вызова нейросетей", s_table_cell)
        ],
        [
            Paragraph("<b>Сайга LLM (Saiga NeMo 12B BF16)</b>", s_table_cell),
            Paragraph("🎮 <b>GPU</b> (CUDA BF16 VRAM)", s_table_cell),
            Paragraph("22.8 ГБ VRAM (на A100 / 48GB)", s_table_cell),
            Paragraph("Высокий. Генерация авторского текста без компромиссов в слоге (35–50 токенов/сек)", s_table_cell)
        ],
        [
            Paragraph("<b>ComfyUI (Qwen-Image BF16 + Realism 2.0)</b>", s_table_cell),
            Paragraph("🎮 <b>GPU</b> (Tensor Cores BF16)", s_table_cell),
            Paragraph("38.1 ГБ VRAM (DiT + VAE + LoRA)", s_table_cell),
            Paragraph("Максимальный. Рендеринг 4-step Lightning фотореалистичного кадра за 3–5 сек", s_table_cell)
        ],
        [
            Paragraph("<b>Moondream2 VLM (Зрение)</b>", s_table_cell),
            Paragraph("🔄 <b>GPU / CPU Fallback</b>", s_table_cell),
            Paragraph("3.5 ГБ VRAM / RAM Fallback", s_table_cell),
            Paragraph("При наплыве очереди автоматически уступает VRAM под ComfyUI", s_table_cell)
        ]
    ]
    t_hw = Table(hw_data, colWidths=[6.8 * cm, 4.8 * cm, 5.2 * cm, 9.7 * cm])
    t_hw.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0, 1), (-1, 3), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (0, 4), (-1, 6), colors.HexColor("#EFF6FF")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_hw)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph(
        "<b>Enterprise & High-Load балансировка:</b> В Enterprise-конфигурации (Tesla A100 80GB / RTX 48GB) система использует неквантованные модели "
        "<b>saiga_nemo_12b.BF16.gguf</b> (22.8 ГБ) и <b>qwen-image-2512-BF16.gguf</b> (38.1 ГБ), которые полностью помещаются в HBM2e память. "
        "На серверах с 24–48 ГБ VRAM интеллектуальный шедулер использует Time-Division Multiplexing: Сайга генерирует текст за 1.5 сек $\\rightarrow$ "
        "память очищается $\\rightarrow$ ComfyUI рендерит фото за 3 сек, гарантируя нулевые задержки при пиковом наплыве.",
        s_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # СЛАЙД 7: ШПАРГАЛКА ДЛЯ ПИТЧА (PITCH CHEAT-SHEET & OBJECTION HANDLING)
    # =========================================================================
    story.append(Paragraph("6. Шпаргалка для питча и ответы на сложные вопросы (Pitch Cheat-Sheet)", s_h1))
    story.append(Paragraph("Готовые тезисы для демонстрации инвесторам, B2B-клиентам и блогерам.", s_subtitle))

    qa_data = [
        [
            Paragraph("<b>Вопрос / Возражение</b>", s_table_hdr),
            Paragraph("<b>Убийственный ответ и Архитектурный пруф (Killer Argument)</b>", s_table_hdr)
        ],
        [
            Paragraph("<b>«Чем вы лучше ChatGPT / Midjourney?»</b>", s_body_bold),
            Paragraph("Обычные нейросети генерируют контент «в вакууме» без памяти. UCust — это <b>замкнутый конвейер с обратной связью</b>: парсер собирает реакции, Moondream считывает цвета, а Сайга адаптирует следующий пост под дефицит сетки 3x3.", s_body)
        ],
        [
            Paragraph("<b>«А если ИИ начнет галлюцинировать и нести бред?»</b>", s_body_bold),
            Paragraph("Защита встроена на уровне пре-фильтра <b>CriticMunger</b>. Он за 1 мс отсекает любые оксюмороны (например, попытки продать «KPI эспрессо» или B2B-термины в зоо-теме).", s_body)
        ],
        [
            Paragraph("<b>«Почему у вас нет чата на фронтенде?»</b>", s_body_bold),
            Paragraph("Потому что чат — это медленно. В UCust клиент тратит <b>30 секунд в день</b> в режиме <b>Action Cards</b>: видит готовый контент-план и подтверждает/меняет его в 1 клик.", s_body)
        ],
        [
            Paragraph("<b>«Как вы не смешиваете данные разных компаний?»</b>", s_body_bold),
            Paragraph("Вся база знаний RAG жестко изолирована по <b>Multi-Tenant Partitioning (tenant_id)</b>. Перекрестная утечка между базой стоматологии и IT-компании математически равна <b>0%</b>.", s_body)
        ],
        [
            Paragraph("<b>«Почему картинки не выглядят как дешевый AI-пластик?»</b>", s_body_bold),
            Paragraph("Мы используем 26-нодовый воркфлоу <b>Realism 2.0</b> с оптикой iPhone 16 Pro (24mm, natural ambient light) и тяжелыми негативными стоп-фильтрами против студийного 3D-глянца.", s_body)
        ]
    ]
    t_qa = Table(qa_data, colWidths=[8.0 * cm, 18.5 * cm])
    t_qa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_qa)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("<b>ИТОГОВЫЙ СЛОГАН ДЛЯ ПИТЧА:</b> «UCust.AI — это автономный контент-завод, где маркетинг управляется математикой, а не случайным вдохновением копирайтера».", s_subtitle))

    # Сборка документа
    doc.build(story, canvasmaker=PitchDeckNumberedCanvas)
    
    # Копирование в корень проекта
    shutil.copy2(pdf_filename_out, pdf_filename_root)
    
    print(f"\n✅ ПРЕЗЕНТАЦИЯ-ПИТЧ УСПЕШНО СГЕНЕРИРОВАНА!")
    print(f"   • Выходной файл 1: {pdf_filename_out} ({os.path.getsize(pdf_filename_out)} bytes)")
    print(f"   • Выходной файл 2: {pdf_filename_root} ({os.path.getsize(pdf_filename_root)} bytes)")

if __name__ == "__main__":
    generate_pitch_deck_pdf()
