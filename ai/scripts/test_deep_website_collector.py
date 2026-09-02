"""
test_deep_website_collector.py
======================================================================
Тестирование 100% готовности WebsiteCollector:
1. Извлечение Schema.org JSON-LD (товары, цены, рейтинги, FAQ).
2. Глубокий рекурсивный сбор страниц 2-го уровня (/services, /catalog, /about).
3. Извлечение контактов, соцсетей и структурирование досье для RAG.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from unittest.mock import patch

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from collectors.website_collector import WebsiteCollector


SAMPLE_MAIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Стоматология «ДентаЛюкс» — Имплантация и Лечение в Москве</title>
    <meta name="description" content="Премиальная стоматологическая клиника на Арбате. Гарантия на импланты 10 лет.">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "MedicalClinic",
        "name": "ДентаЛюкс",
        "telephone": "+7 (495) 777-22-33",
        "priceRange": "₽₽₽",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Москва",
            "streetAddress": "ул. Новый Арбат, 15"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "128"
        }
    }
    </script>
</head>
<body>
    <header>
        <img src="/assets/img/logo.svg" alt="Логотип ДентаЛюкс">
        <nav>
            <a href="/uslugi">Все услуги</a>
            <a href="/catalog/implants">Имплантация</a>
            <a href="/o-nas">О клинике</a>
            <a href="/contacts">Контакты</a>
            <a href="/login">Личный кабинет</a>
        </nav>
    </header>
    <main>
        <h1>Премиальная стоматология полного цикла</h1>
        <h2>Немецкое оборудование KaVo и 3D-томография</h2>
        <p>Мы работаем с 2012 года, восстанавливая улыбки любой сложности без боли и страха.</p>
        <p>В нашей команде хирурги и ортодонты высшей категории со стажем от 10 лет.</p>
        <img src="https://dentalux-mock.ru/images/product-implant-straumann.jpg" alt="Швейцарские импланты Straumann" class="service-photo">
    </main>
    <footer>
        <a href="https://t.me/dentalux_msk">Telegram канал</a>
        <a href="https://vk.com/dentalux_official">Группа ВКонтакте</a>
        <a href="https://wa.me/79991112233">Запись в WhatsApp</a>
    </footer>
</body>
</html>"""

SAMPLE_SERVICES_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Услуги и цены клиники ДентаЛюкс</title>
    <script type="application/ld+json">
    [
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Имплантация Straumann BLX под ключ",
            "description": "Швейцарский премиальный имплант с коронкой из диоксида циркония",
            "offers": {
                "@type": "Offer",
                "price": "65000",
                "priceCurrency": "RUB"
            }
        },
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Профессиональная чистка Air-Flow Pro",
            "description": "Снятие налета и полировка эмали",
            "offers": {
                "@type": "Offer",
                "price": "7500",
                "priceCurrency": "RUB"
            }
        }
    ]
    </script>
</head>
<body>
    <h1>Прайс-лист и популярные услуги</h1>
    <h2>Имплантация зубов</h2>
    <p>Установка дентальных имплантов ведущих мировых брендов: Straumann (Швейцария), Osstem (Южная Корея).</p>
</body>
</html>"""


async def test_website_collector_full():
    print("=" * 80)
    print("🌐 ТЕСТИРОВАНИЕ 100% ГОТОВНОСТИ WEBSITE COLLECTOR (DEEP CRAWL + SCHEMA.ORG)")
    print("=" * 80)

    collector = WebsiteCollector()

    # Мокаем скачивание HTTP
    async def mock_fetch(url: str):
        if "/uslugi" in url or "/catalog" in url:
            return SAMPLE_SERVICES_PAGE, url, "success"
        elif "/o-nas" in url:
            return "<html><body><h1>О клинике</h1><p>Опыт работы 12 лет, более 10 000 довольных пациентов.</p></body></html>", url, "success"
        elif "/contacts" in url:
            return "<html><body><h1>Контакты</h1><p>г. Москва, ул. Новый Арбат, 15. Тел: +7 (495) 777-22-33</p></body></html>", url, "success"
        else:
            return SAMPLE_MAIN_PAGE, url, "success"

    collector._fetch_html_async = mock_fetch

    # Запуск сбора сайта
    result = await collector.collect_website_async("https://dentalux-mock.ru", deep_crawl=True)

    print("\n--- Результаты глубокого сбора ---")
    assert result["status"] == "success"
    print(f"✅ Название сайта: {result['title']}")
    print(f"✅ УТП/Описание: {result['description']}")
    
    # 1. Проверка Schema.org
    schema = result["schema_data"]
    b_info = schema.get("business_info", {})
    print(f"✅ Schema.org Рейтинг: {b_info.get('rating')}")
    print(f"✅ Schema.org Адрес: {b_info.get('address')}")
    print(f"✅ Schema.org Телефон: {b_info.get('phone')}")
    assert "4.9" in b_info.get("rating", "")
    assert "Новый Арбат" in b_info.get("address", "")

    # 2. Проверка товаров и прайса из Schema.org
    products = result["products"]
    print(f"\n✅ Извлечено товаров/услуг: {len(products)}")
    for p in products:
        print(f"   • {p['name']} -> {p['price']}")
    assert len(products) >= 2
    assert any("Straumann" in p["name"] for p in products)

    # 3. Проверка рекурсивно собранных подстраниц
    subpages = result["subpages_data"]
    print(f"\n✅ Глубокий сбор страниц 2-го уровня ({len(subpages)} стр.):")
    for sp in subpages:
        print(f"   • Раздел: {sp['path']} (Заголовок: '{sp['title']}')")
    assert len(subpages) >= 2

    # 4. Проверка соцсетей
    socials = result["social_links"]
    print(f"\n✅ Соцсети: TG={socials['telegram']}, VK={socials['vk']}, WA={socials['whatsapp']}")
    assert len(socials["telegram"]) > 0
    assert len(socials["vk"]) > 0

    # 5. Проверка финального структурированного досье для RAG
    dossier = result["structured_dossier"]
    print("\n" + "=" * 50)
    print("📑 ФИНАЛЬНОЕ СТРУКТУРИРОВАННОЕ ДОСЬЕ ДЛЯ CLEAN RAG:")
    print("=" * 50)
    print(dossier)
    print("=" * 50)

    assert "Каталог товаров и прайс-лист" in dossier
    assert "Рейтинг клиентов" in dossier
    assert "Данные ключевых разделов сайта" in dossier

    print("\n🎉 ВСЕ ТЕСТЫ 100% WEBSITE COLLECTOR УСПЕШНО ПРОЙДЕНЫ!")


if __name__ == "__main__":
    asyncio.run(test_website_collector_full())
