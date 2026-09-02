"""
test_smart_bridge_and_quick_search.py
======================================================================
Тестирование реального кейса:
Сайт-визитка maksima.uz (1 страница) с кнопкой перехода
в основной интернет-магазин status.uz (посуда + раздел мебели).
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

# 1. Тонкий сайт-визитка Maksima.uz (1 страница, кнопка перехода на status.uz)
MAKSIMA_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Maksima Мебель Ташкент</title>
    <meta name="description" content="Шоурум дизайнерской мебели Maksima в Ташкенте.">
</head>
<body>
    <header>
        <img src="/logo.svg" alt="Maksima Logo">
    </header>
    <main>
        <h1>Maksima — Премиальная мебель для дома</h1>
        <p>Наш онлайн-каталог и оформление заказов переехали в единый маркетплейс Status.uz!</p>
        <div class="cta-box">
            <a href="https://status.uz/mebel" class="btn btn-primary">Перейти в каталог мебели на Status.uz</a>
        </div>
    </main>
    <footer>
        <p>Телефон: +998 (71) 200-11-22</p>
        <a href="https://t.me/maksima_uz">Telegram</a>
    </footer>
</body>
</html>"""

# 2. Основной интернет-магазин Status.uz (посуда и раздел мебели)
STATUS_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Status.uz — Премиальная посуда и мебель в Узбекистане</title>
    <meta name="description" content="Крупнейший интернет-магазин элитной посуды и европейской мебели в Ташкенте.">
    <script type="application/ld+json">
    [
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Обеденный стол Maksima Grand Wood",
            "description": "Массив дуба, шпонированная столешница, 8 персон",
            "offers": {
                "@type": "Offer",
                "price": "12500000",
                "priceCurrency": "UZS"
            }
        },
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Диван угловой Maksima Soft Velvet",
            "description": "Итальянский велюр, раскладной механизм",
            "offers": {
                "@type": "Offer",
                "price": "18900000",
                "priceCurrency": "UZS"
            }
        },
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Набор фарфоровой посуды Wilmax 24 предмета",
            "description": "Английский фарфор премиум качества",
            "offers": {
                "@type": "Offer",
                "price": "3400000",
                "priceCurrency": "UZS"
            }
        }
    ]
    </script>
</head>
<body>
    <h1>Интернет-магазин Status.uz</h1>
    <h2>Разделы: Посуда, Мебель Maksima, Текстиль, Декор</h2>
    <p>Доставка по всему Ташкенту и регионам Узбекистана. Шоурум: ул. Амира Темура, 45.</p>
    <a href="https://instagram.com/status.uz">Instagram</a>
</body>
</html>"""


async def run_bridge_test():
    print("=" * 80)
    print("🌉 ТЕСТ SMART BRIDGE ROUTER: ПЕРЕХОД С САЙТА-ВИЗИТКИ В ОСНОВНОЙ МАГАЗИН")
    print("=" * 80)

    collector = WebsiteCollector()

    # Мокаем скачивание URL
    async def mock_fetch(url: str):
        if "maksima.uz" in url:
            return MAKSIMA_HTML, "https://maksima.uz/", "success"
        elif "status.uz" in url:
            return STATUS_HTML, "https://status.uz/mebel", "success"
        return "<html><body>Page</body></html>", url, "success"

    collector._fetch_html_async = mock_fetch

    # Запускаем сбор с сайта-визитки Maksima
    result = await collector.collect_website_async("https://maksima.uz/", deep_crawl=True, follow_bridge=True)

    print("\n--- Проверка результатов сбора ---")
    assert result["status"] == "success"
    print(f"✅ Исходный сайт: {result['url']}")
    print(f"✅ Название: {result['title']}")
    print(f"✅ Мост обнаружен: {result['bridge_store'] is not None}")
    
    bridge = result["bridge_store"]
    assert bridge is not None
    print(f"✅ Адрес основного магазина: {bridge['url']}")
    print(f"✅ Описание магазина: {bridge['description']}")

    # Проверка объединенных товаров
    products = result["products"]
    print(f"\n✅ Объединенный каталог товаров ({len(products)} поз.):")
    for p in products:
        print(f"   • {p['name']} -> {p['price']}")
    
    assert len(products) >= 3
    assert any("Maksima Grand Wood" in p["name"] for p in products)
    assert any("Wilmax" in p["name"] for p in products)

    # Проверка контактов и соцсетей
    phones = result["contacts"]["phones"]
    socials = result["social_links"]
    print(f"\n✅ Контакты: {phones}")
    print(f"✅ Соцсети: TG={socials['telegram']}, Instagram={socials['instagram']}")
    assert "+998 (71) 200-11-22" in phones
    assert any("status.uz" in s for s in socials["instagram"])

    # Проверка RAG-досье
    dossier = result["structured_dossier"]
    print("\n" + "=" * 50)
    print("📑 СИНТЕЗИРОВАННОЕ ДОСЬЕ ДЛЯ RAG (Maksima + Status.uz):")
    print("=" * 50)
    print(dossier)
    print("=" * 50)

    assert "СВЯЗАННЫЙ ОСНОВНОЙ ИНТЕРНЕТ-МАГАЗИН: https://status.uz/mebel" in dossier
    assert "Maksima Grand Wood" in dossier
    assert "Wilmax" in dossier

    print("\n🎉 ТЕСТ SMART BRIDGE ROUTER УСПЕШНО ПРОЙДЕН!")


if __name__ == "__main__":
    asyncio.run(run_bridge_test())
