"""
test_content_image_filter.py
======================================================================
Тестирование строгого отсева логотипов, шапок, баннеров и иконок
с сохранением только реальных товаров, портфолио и контентных фото.
======================================================================
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
from PIL import Image

AI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)

from collectors.website_collector import CleanHTMLParser, WebsiteCollector


def test_html_parser_image_filtering():
    print("=" * 80)
    print("🧪 ТЕСТ ФИЛЬТРАЦИИ ИЗОБРАЖЕНИЙ: ТОВАРЫ/КОНТЕНТ VS ЛОГО/ШАПКИ")
    print("=" * 80)

    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Автосалон и Детейлинг 'GrandMotors'</title>
        <meta property="og:image" content="https://example.com/assets/og_hero_banner.jpg">
    </head>
    <body>
        <header>
            <img src="https://example.com/static/img/site_logo_main.svg" alt="Company Logo" class="brand-logo">
            <img src="https://example.com/images/header_nav_banner.jpg" class="top-banner">
        </header>

        <nav>
            <img src="https://example.com/icons/menu_arrow.png" alt="icon">
        </nav>

        <main>
            <h1>Премиальный уход за вашим автомобилем</h1>
            
            <!-- Контентные фото и карточки товаров / услуг -->
            <div class="catalog-grid">
                <div class="product-card">
                    <img src="https://example.com/catalog/goods/bmw_ceramic_coating_4k.jpg" alt="Керамическое покрытие BMW M5" class="product-item-img">
                </div>
                <div class="portfolio-item">
                    <img src="https://example.com/gallery/porsche_detailing_stage1.jpg" alt="Полировка кузова Porsche 911" class="gallery-photo">
                </div>
                <div class="service-case">
                    <img src="https://example.com/services/interior_dry_cleaning_real.jpg" alt="Химчистка салона автомобиля" class="content-work-photo">
                </div>
            </div>

            <!-- Служебный мусор, аватары и кнопки -->
            <aside>
                <img src="https://example.com/avatar/user123.png" class="author-avatar">
                <img src="https://example.com/btn/book_button.png" class="btn-img">
            </aside>
        </main>

        <footer>
            <img src="https://example.com/footer/footer_logo.png" class="footer-brand">
            <img src="https://example.com/partners/bank_partner_logo.png" class="sponsor-logo">
        </footer>
    </body>
    </html>
    """

    parser = CleanHTMLParser()
    parser.feed(sample_html)

    # Проверка отсева логотипов и шапок
    collector = WebsiteCollector()
    
    LOGO_BANNER_EXCLUSIONS = {
        'logo', 'logotype', 'brand', 'header', 'hero', 'banner', 'top-banner', 'site-banner',
        'title-bg', 'favicon', 'icon', 'avatar', 'footer', 'badge', 'button', 'btn', 'arrow',
        'separator', 'divider', 'placeholder', 'blank', 'transparent', '1x1', 'pixel', 'advert',
        'tracker', 'vk-share', 'tg-share', 'social', 'widget', 'author', 'partner', 'sponsor'
    }
    PRODUCT_CONTENT_KEYWORDS = {
        'product', 'item', 'catalog', 'service', 'goods', 'portfolio', 'gallery', 'work',
        'project', 'case', 'photo', 'content', 'card', 'article', 'post', 'feed', 'real',
        'preview', 'detail', 'sample', 'master', 'car', 'dish', 'room', 'interior', 'doctor'
    }

    filtered_candidates = []
    for item in parser.image_items:
        if item.get('in_skip_container'):
            continue
        src = item.get('src', '')
        combined = f"{src} {item.get('alt', '')} {item.get('class', '')} {item.get('id', '')}".lower()
        
        if any(exc in combined for exc in LOGO_BANNER_EXCLUSIONS):
            continue
        if any(kw in combined for kw in PRODUCT_CONTENT_KEYWORDS):
            filtered_candidates.append(src)

    print(f"📷 Всего изображений в HTML: {len(parser.image_items)}")
    print(f"🎯 Отобрано контентных фото товаров/портфолио: {len(filtered_candidates)}")
    for f in filtered_candidates:
        print(f"   • {f}")

    # Проверки
    assert len(filtered_candidates) == 3, f"Ожидалось 3 контентных фото, получено {len(filtered_candidates)}"
    assert any("bmw_ceramic_coating" in f for f in filtered_candidates)
    assert any("porsche_detailing" in f for f in filtered_candidates)
    assert any("interior_dry_cleaning" in f for f in filtered_candidates)

    # Ни одного логотипа или шапки не должно пройти
    for f in filtered_candidates:
        assert "logo" not in f.lower()
        assert "banner" not in f.lower()
        assert "avatar" not in f.lower()
        assert "button" not in f.lower()

    print("\n" + "=" * 80)
    print("🎉 ТЕСТ СТРОГОГО ОТБОРА ТОВАРОВ И КОНТЕНТА УСПЕШНО ПРОЙДЕН!")
    print("=" * 80)


if __name__ == "__main__":
    test_html_parser_image_filtering()
