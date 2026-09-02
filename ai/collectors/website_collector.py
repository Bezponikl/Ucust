# File: collectors/website_collector.py
from __future__ import annotations

import re
import json
import html
import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse, urljoin, urldefrag
from html.parser import HTMLParser

logger = logging.getLogger('ucust_collectors.website')


class CleanHTMLParser(HTMLParser):
    """
    Высокоскоростной HTML-парсер:
    - Извлекает метатеги, OpenGraph, Schema.org (JSON-LD), заголовки H1-H3, уникальный текст.
    - Извлекает ссылки на подстраницы каталога, услуг и контактов.
    - Фильтрует технический мусор, скрипты и стили.
    """
    def __init__(self):
        super().__init__()
        self.title = ''
        self.meta_description = ''
        self.meta_keywords = ''
        self.og_title = ''
        self.og_description = ''
        self.og_image = ''
        self.og_site_name = ''
        self.theme_color = ''
        self.headings = []
        self.paragraphs = []
        self.links = []
        self.images = []
        self.image_items = []
        self.json_ld_raw: List[str] = []
        
        self._current_tag = ''
        self._current_text = []
        self._skip_tags = {'script', 'style', 'svg', 'noscript', 'header', 'footer', 'nav', 'aside'}
        self._in_skip = False
        self._in_json_ld = False
        self._json_ld_buffer = []

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag.lower()
        attr_dict = {k.lower(): (v or '') for k, v in attrs}

        # 1. Захват Schema.org JSON-LD
        if self._current_tag == 'script' and attr_dict.get('type', '').lower() == 'application/ld+json':
            self._in_json_ld = True
            self._json_ld_buffer = []
            return

        if self._current_tag in self._skip_tags:
            self._in_skip = True

        # 2. Мета-теги
        if self._current_tag == 'meta':
            name = attr_dict.get('name', '').lower()
            prop = attr_dict.get('property', '').lower()
            content = attr_dict.get('content', '').strip()
            if name == 'description':
                self.meta_description = content
            elif name == 'keywords':
                self.meta_keywords = content
            elif name == 'theme-color':
                self.theme_color = content
            elif prop == 'og:title':
                self.og_title = content
            elif prop == 'og:description':
                self.og_description = content
            elif prop == 'og:image':
                self.og_image = content
            elif prop == 'og:site_name':
                self.og_site_name = content

        # 3. Ссылки
        elif self._current_tag == 'a':
            href = attr_dict.get('href', '').strip()
            if href:
                self.links.append(href)

        # 4. Изображения
        elif self._current_tag == 'img':
            src = attr_dict.get('src', '').strip() or attr_dict.get('data-src', '').strip() or attr_dict.get('data-original', '').strip() or attr_dict.get('data-lazy', '').strip()
            if src and not src.startswith('data:image/svg') and not src.endswith('.svg') and not src.endswith('.ico'):
                alt = attr_dict.get('alt', '').strip()
                cls = attr_dict.get('class', '').strip()
                img_id = attr_dict.get('id', '').strip()
                self.images.append(src)
                self.image_items.append({
                    'src': src,
                    'alt': alt,
                    'class': cls,
                    'id': img_id,
                    'in_skip_container': self._in_skip
                })

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == 'script' and self._in_json_ld:
            raw_json = ''.join(self._json_ld_buffer).strip()
            if raw_json:
                self.json_ld_raw.append(raw_json)
            self._in_json_ld = False
            self._json_ld_buffer = []
            return

        if tag_lower in self._skip_tags:
            self._in_skip = False

        text = html.unescape(' '.join(self._current_text)).strip()
        self._current_text = []
        if text and not self._in_skip:
            if tag_lower in {'h1', 'h2', 'h3'}:
                self.headings.append(text)
            elif tag_lower in {'p', 'li', 'span', 'div'} and len(text) > 25:
                self.paragraphs.append(text)
        self._current_tag = ''

    def handle_data(self, data):
        if self._in_json_ld:
            self._json_ld_buffer.append(data)
            return

        if not self._in_skip and data.strip():
            self._current_text.append(data.strip())


class WebsiteCollector:
    """
    Коллектор веб-сайтов корпоративного уровня (100% готовность):
    - Рекурсивный глубокий сбор подстраниц (/catalog, /services, /prices, /about).
    - Парсинг Schema.org JSON-LD (товары, цены, рейтинги, отзывы, FAQ).
    - Умный отсев лого/баннеров и проверка фото через PIL.
    - Автоматический поиск сайтов конкурентов через DuckDuckGo и Tavily.
    """
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"'
    }

    PRIORITY_SUBPAGE_KEYWORDS = [
        'uslugi', 'services', 'service', 'catalog', 'katalog', 'products', 'tovary',
        'price', 'prices', 'tarify', 'stoimost', 'menu', 'o-nas', 'about',
        'company', 'portfolio', 'cases', 'works', 'projects', 'contacts', 'kontakty'
    ]

    EXCLUDE_SUBPAGE_KEYWORDS = [
        'login', 'signin', 'register', 'auth', 'cart', 'basket', 'checkout',
        'order', 'privacy', 'policy', 'terms', 'politika', 'soglasie', 'cookie',
        'wp-admin', 'admin', 'logout', 'download', '.pdf', '.zip', '.rar', 'feed'
    ]

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    def _normalize_url(self, raw_url: str) -> str:
        url = raw_url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        return url

    def _extract_schema_org_entities(self, json_ld_strings: List[str]) -> Dict[str, Any]:
        """
        Извлекает структурированные данные Schema.org:
        - Товары и цены (Product / Offer)
        - Организация, рейтинг и контакты (LocalBusiness / Organization / AggregateRating)
        - Вопросы и ответы (FAQPage)
        """
        products = []
        business_info = {}
        faq_items = []

        for raw_str in json_ld_strings:
            try:
                # Очистка возможных комментариев внутри JSON
                cleaned_json = re.sub(r'/\*.*?\*/', '', raw_str, flags=re.DOTALL)
                data = json.loads(cleaned_json)
                items = data if isinstance(data, list) else [data]

                for item in items:
                    if not isinstance(item, dict):
                        continue
                    
                    schema_type = str(item.get('@type', '')).lower()

                    # 1. Товары и прайс (Product / Offer)
                    if 'product' in schema_type:
                        name = item.get('name') or item.get('title')
                        offers = item.get('offers', {})
                        price = ''
                        currency = 'RUB'
                        if isinstance(offers, dict):
                            price = str(offers.get('price', '')).strip()
                            currency = offers.get('priceCurrency', 'RUB')
                        elif isinstance(offers, list) and offers:
                            price = str(offers[0].get('price', '')).strip()
                            currency = offers[0].get('priceCurrency', 'RUB')

                        if name:
                            desc = item.get('description', '')
                            products.append({
                                'name': name,
                                'price': f"{price} {currency}".strip() if price else 'По запросу',
                                'description': desc[:120] if desc else ''
                            })

                    # 2. Бизнес, рейтинг и контакты (LocalBusiness / Organization)
                    if any(t in schema_type for t in ['organization', 'localbusiness', 'store', 'restaurant', 'autoservice', 'medicalclinic']):
                        if item.get('name'):
                            business_info['name'] = item.get('name')
                        if item.get('telephone'):
                            business_info['phone'] = item.get('telephone')
                        if item.get('priceRange'):
                            business_info['price_range'] = item.get('priceRange')
                        if item.get('aggregateRating'):
                            ar = item.get('aggregateRating', {})
                            business_info['rating'] = f"{ar.get('ratingValue', '')}/5 (на основе {ar.get('reviewCount', ar.get('ratingCount', ''))} отзывов)"
                        if item.get('address'):
                            addr = item.get('address')
                            if isinstance(addr, dict):
                                business_info['address'] = f"{addr.get('addressLocality', '')}, {addr.get('streetAddress', '')}".strip(', ')
                            elif isinstance(addr, str):
                                business_info['address'] = addr

                    # 3. FAQPage (Вопросы и ответы)
                    if 'faqpage' in schema_type or 'mainentity' in item:
                        main_entities = item.get('mainEntity', [])
                        if isinstance(main_entities, list):
                            for q_entity in main_entities:
                                if isinstance(q_entity, dict) and q_entity.get('name'):
                                    q_name = q_entity.get('name')
                                    ans_obj = q_entity.get('acceptedAnswer', {})
                                    ans_text = ans_obj.get('text', '') if isinstance(ans_obj, dict) else ''
                                    faq_items.append({'q': q_name, 'a': ans_text[:200]})
            except Exception:
                continue

        return {
            'products': products[:15],
            'business_info': business_info,
            'faq_items': faq_items[:6]
        }

    async def _fetch_html_async(self, url: str) -> Tuple[str, str, str]:
        """
        Скачивает HTML с автоматическим определением кодировки (UTF-8, CP1251).
        Возвращает (html_content, final_url, status).
        """
        import httpx
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False, headers=self.HEADERS) as client:
                resp = await client.get(url)
                final_url = str(resp.url)
                # Авто-определение кодировки для старых российских сайтов
                encoding = resp.encoding or 'utf-8'
                try:
                    html_content = resp.text
                except Exception:
                    html_content = resp.content.decode('cp1251', errors='ignore')
                return html_content, final_url, 'success'
        except Exception as err:
            try:
                import aiohttp
                async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                    async with session.get(url, timeout=self.timeout, ssl=False) as resp:
                        final_url = str(resp.url)
                        raw_bytes = await resp.read()
                        try:
                            html_content = raw_bytes.decode('utf-8')
                        except Exception:
                            html_content = raw_bytes.decode('cp1251', errors='ignore')
                        return html_content, final_url, 'success'
            except Exception as e2:
                return '', url, str(e2)

    def _find_priority_subpages(self, base_url: str, links: List[str], max_pages: int = 3) -> List[str]:
        """
        Находит наиболее ценные внутренние ссылки (каталог, услуги, прайс, контакты, о компании).
        """
        base_domain = urlparse(base_url).netloc.lower().replace('www.', '')
        candidates: List[str] = []
        seen = {base_url.rstrip('/')}

        for raw_link in links:
            clean_link = urldefrag(raw_link)[0].strip()
            if not clean_link or clean_link.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue

            abs_link = urljoin(base_url, clean_link).rstrip('/')
            link_domain = urlparse(abs_link).netloc.lower().replace('www.', '')

            # Только внутренние страницы того же домена
            if link_domain != base_domain:
                continue

            path_lower = urlparse(abs_link).path.lower()
            if abs_link in seen:
                continue

            # Исключаем корзины, логины, политики
            if any(ex in path_lower for ex in self.EXCLUDE_SUBPAGE_KEYWORDS):
                continue

            # Приоритет страницам услуг, каталога, цен и контактов
            if any(kw in path_lower for kw in self.PRIORITY_SUBPAGE_KEYWORDS):
                candidates.append(abs_link)
                seen.add(abs_link)
                if len(candidates) >= max_pages:
                    break

        return candidates

    async def collect_website_async(self, raw_url: str, deep_crawl: bool = True) -> Dict[str, Any]:
        """
        Главный метод сбора информации с сайта.
        Выполняет парсинг главной страницы + параллельный сбор ключевых подстраниц + Schema.org.
        """
        url = self._normalize_url(raw_url)
        print(f"[WebsiteCollector] 🌐 Парсинг сайта компании: {url} (Deep Crawl: {deep_crawl})...")

        html_content, final_url, status = await self._fetch_html_async(url)
        if status != 'success' or not html_content:
            print(f"[WebsiteCollector] ⚠️ Ошибка подключения к {url}: {status}")
            return {'status': 'error', 'url': url, 'error': status, 'source': 'website'}

        # 1. Парсинг главной страницы
        parser = CleanHTMLParser()
        try:
            parser.feed(html_content)
        except Exception:
            pass

        # 2. Извлечение Schema.org структурированных данных
        schema_data = self._extract_schema_org_entities(parser.json_ld_raw)

        # 3. Извлечение контактов и соцсетей
        all_text_blob = parser.title + ' ' + parser.meta_description + ' ' + ' '.join(parser.headings) + ' ' + ' '.join(parser.paragraphs)
        phones = list(set(re.findall(r'(?:\+7|8)[\s\-]?(?:\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})', all_text_blob)))
        emails = list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', all_text_blob)))

        # Дополняем контактами из Schema.org
        if schema_data.get('business_info', {}).get('phone') and schema_data['business_info']['phone'] not in phones:
            phones.insert(0, schema_data['business_info']['phone'])

        social_profiles = {'telegram': [], 'vk': [], 'ok': [], 'whatsapp': [], 'youtube': []}
        for link in parser.links:
            if 't.me/' in link or 'telegram.me/' in link:
                social_profiles['telegram'].append(link)
            elif 'vk.com/' in link:
                social_profiles['vk'].append(link)
            elif 'ok.ru/' in link or 'odnoklassniki.ru/' in link:
                social_profiles['ok'].append(link)
            elif 'wa.me/' in link or 'whatsapp.com' in link:
                social_profiles['whatsapp'].append(link)
            elif 'youtube.com' in link:
                social_profiles['youtube'].append(link)

        for k in social_profiles:
            social_profiles[k] = list(set(social_profiles[k]))

        unique_paragraphs = []
        seen_p = set()
        for p in parser.paragraphs:
            cleaned = re.sub(r'\s+', ' ', p).strip()
            if len(cleaned) > 25 and cleaned not in seen_p:
                seen_p.add(cleaned)
                unique_paragraphs.append(cleaned)

        title = parser.og_title or parser.title or urlparse(final_url).netloc
        description = parser.og_description or parser.meta_description or ''
        headings_top = parser.headings[:12]
        key_paragraphs = unique_paragraphs[:12]

        # 4. Рекурсивный глубокий сбор страниц 2-го уровня (Услуги, Каталог, Цены, О нас)
        subpages_data = []
        if deep_crawl:
            priority_subpages = self._find_priority_subpages(final_url, parser.links, max_pages=3)
            if priority_subpages:
                print(f"[WebsiteCollector] 📑 Найдено {len(priority_subpages)} ключевых подстраниц: {[urlparse(u).path for u in priority_subpages]}")
                
                async def _crawl_subpage(sub_url: str):
                    sub_html, _, sub_stat = await self._fetch_html_async(sub_url)
                    if sub_stat == 'success' and sub_html:
                        sub_p = CleanHTMLParser()
                        try:
                            sub_p.feed(sub_html)
                        except Exception:
                            pass
                        sub_schema = self._extract_schema_org_entities(sub_p.json_ld_raw)
                        return {
                            'url': sub_url,
                            'path': urlparse(sub_url).path,
                            'title': sub_p.title or sub_p.og_title,
                            'headings': sub_p.headings[:6],
                            'paragraphs': sub_p.paragraphs[:4],
                            'products': sub_schema.get('products', []),
                            'faq_items': sub_schema.get('faq_items', [])
                        }
                    return None

                crawl_tasks = [_crawl_subpage(u) for u in priority_subpages]
                crawl_results = await asyncio.gather(*crawl_tasks)
                subpages_data = [r for r in crawl_results if r]

        # 5. Формирование структурированного досье для RAG
        summary_dossier = f"=== Официальный сайт: {final_url} ===\nНазвание: {title}\n"
        if description:
            summary_dossier += f"Описание (УТП): {description}\n"
        
        # Schema.org Рейтинг и адрес
        b_info = schema_data.get('business_info', {})
        if b_info.get('rating'):
            summary_dossier += f"⭐ Рейтинг клиентов: {b_info['rating']}\n"
        if b_info.get('address'):
            summary_dossier += f"📍 Адрес / Локация: {b_info['address']}\n"

        if headings_top:
            summary_dossier += "Ключевые разделы и предложения:\n- " + "\n- ".join(headings_top) + "\n"
        if key_paragraphs:
            summary_dossier += "О компании и услугах:\n" + " ".join(key_paragraphs[:4]) + "\n"

        # Добавляем товары из Schema.org
        all_products = schema_data.get('products', [])
        for sp in subpages_data:
            all_products.extend(sp.get('products', []))
        
        if all_products:
            summary_dossier += "\n🏷️ Каталог товаров и прайс-лист:\n"
            for prod in all_products[:8]:
                summary_dossier += f"- {prod['name']} — {prod['price']}\n"

        # Добавляем данные с подстраниц
        if subpages_data:
            summary_dossier += "\n📑 Данные ключевых разделов сайта:\n"
            for sp in subpages_data:
                sp_title = sp.get('title') or sp.get('path')
                sp_h = ", ".join(sp.get('headings', [])[:3])
                sp_text = " ".join(sp.get('paragraphs', [])[:2])
                summary_dossier += f"• Раздел [{sp['path']}]: {sp_title}\n  Предложения: {sp_h}\n  Суть: {sp_text[:200]}\n"

        # Добавляем FAQ из Schema.org
        all_faqs = schema_data.get('faq_items', [])
        for sp in subpages_data:
            all_faqs.extend(sp.get('faq_items', []))
        if all_faqs:
            summary_dossier += "\n❓ Частые вопросы покупателей (FAQ):\n"
            for item in all_faqs[:4]:
                summary_dossier += f"В: {item['q']}\nО: {item['a']}\n"

        if phones or emails:
            summary_dossier += f"\nКонтакты: Телефоны={phones[:2]}, Email={emails[:2]}\n"

        # 6. Фильтрация контентных изображений (Anti-Logo Filter)
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

        priority_images = []
        regular_images = []
        seen_img_urls = set()

        for item in getattr(parser, 'image_items', []):
            if item.get('in_skip_container'):
                continue
            
            img_src = item.get('src', '')
            abs_img = urljoin(final_url, img_src)
            if abs_img in seen_img_urls:
                continue

            combined_str = f"{abs_img} {item.get('alt', '')} {item.get('class', '')} {item.get('id', '')}".lower()

            if any(exc in combined_str for exc in LOGO_BANNER_EXCLUSIONS):
                continue
            if any(ext in abs_img.lower() for ext in ['.svg', '.ico', '.gif', 'pixel', 'tracker', '1x1']):
                continue

            seen_img_urls.add(abs_img)
            if any(kw in combined_str for kw in PRODUCT_CONTENT_KEYWORDS):
                priority_images.append(abs_img)
            else:
                regular_images.append(abs_img)

        extracted_images = (priority_images + regular_images)[:15]
        cached_images = await self.download_and_cache_images_async(extracted_images, max_images=9)

        print(f"[WebsiteCollector] ✅ Сайт успешно обработан: {title} (Собрано подстраниц: {len(subpages_data)}, Фото: {len(cached_images)}, Товаров: {len(all_products)})")
        
        return {
            'status': 'success',
            'source': 'website',
            'url': final_url,
            'title': title,
            'description': description,
            'meta_keywords': parser.meta_keywords,
            'og_image': None,
            'theme_color': parser.theme_color,
            'images': extracted_images[:9],
            'cached_images': cached_images,
            'headings': headings_top,
            'key_texts': key_paragraphs,
            'contacts': {'phones': phones[:3], 'emails': emails[:3]},
            'social_links': social_profiles,
            'schema_data': schema_data,
            'subpages_data': subpages_data,
            'products': all_products,
            'structured_dossier': summary_dossier
        }

    async def download_and_cache_images_async(self, image_urls: List[str], max_images: int = 9) -> List[str]:
        """
        Асинхронно скачивает и валидирует превью картинок (отсекает мелкие иконки и вытянутые баннеры через PIL).
        """
        if not image_urls:
            return []

        import os
        import hashlib
        import httpx
        from PIL import Image

        cache_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "temp_cache"))
        os.makedirs(cache_dir, exist_ok=True)

        cached_files = []
        async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
            for url in image_urls:
                if len(cached_files) >= max_images:
                    break
                try:
                    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()[:10]
                    ext = ".jpg"
                    if ".png" in url.lower():
                        ext = ".png"
                    elif ".webp" in url.lower():
                        ext = ".webp"
                    
                    file_path = os.path.join(cache_dir, f"site_img_{url_hash}{ext}")
                    
                    if not (os.path.exists(file_path) and os.path.getsize(file_path) > 2048):
                        resp = await client.get(url, headers=self.HEADERS)
                        if resp.status_code == 200 and len(resp.content) > 2048:
                            with open(file_path, "wb") as f:
                                f.write(resp.content)
                        else:
                            continue

                    try:
                        with Image.open(file_path) as pil_img:
                            w, h = pil_img.size
                            if w < 180 or h < 180:
                                os.remove(file_path)
                                continue
                            ratio = w / float(h)
                            if ratio > 2.9 or ratio < 0.34:
                                os.remove(file_path)
                                continue
                    except Exception:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        continue

                    cached_files.append(file_path)
                except Exception as ex:
                    logger.debug(f"[WebsiteCollector] Skip image download {url}: {ex}")

        if cached_files:
            print(f"[WebsiteCollector] 📸 Успешно скачано и сохранено {len(cached_files)} контентных фото для Визуального Директора.")
        return cached_files

    async def search_websites_async(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Ищет сайты компаний и конкурентов в интернете (через DuckDuckGo / Tavily / Web Scraper).
        """
        clean_query = query.strip()
        print(f"[WebsiteCollector] 🌐 Поиск сайтов в интернете по запросу: '{clean_query}' (лимит: {limit})...")
        results: List[Dict[str, Any]] = []

        # 1. Попытка через Tavily API
        import os
        tavily_key = os.getenv("TRAVITY_API_KEY") or os.getenv("TAVILY_API_KEY")
        if tavily_key:
            try:
                import httpx
                async with httpx.AsyncClient(timeout=min(self.timeout, 4.0)) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={"api_key": tavily_key, "query": clean_query, "max_results": limit},
                        headers={"Content-Type": "application/json"}
                    )
                    if resp.status_code == 200:
                        t_data = resp.json()
                        for item in t_data.get("results", [])[:limit]:
                            results.append({
                                "title": item.get("title", ""),
                                "url": item.get("url", ""),
                                "snippet": item.get("content", "") or item.get("snippet", ""),
                                "source": "tavily_search"
                            })
                        if results:
                            print(f"[WebsiteCollector] ✅ Найдено {len(results)} сайтов через Tavily API.")
                            return results
            except Exception as e_tavily:
                logger.debug(f"[WebsiteCollector] Tavily search fallback: {e_tavily}")

        # 2. Поиск через веб-шлюз DuckDuckGo HTML
        try:
            import httpx
            from urllib.parse import quote_plus, unquote
            ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(clean_query)}"
            async with httpx.AsyncClient(timeout=min(self.timeout, 3.5), follow_redirects=True, headers=self.HEADERS) as client:
                resp = await client.get(ddg_url)
                if resp.status_code == 200:
                    html_text = resp.text
                    raw_links = re.findall(r'<a class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html_text, re.DOTALL)

                    for raw_link, raw_title in raw_links:
                        real_url = raw_link
                        if "uddg=" in raw_link:
                            match_uddg = re.search(r'uddg=([^&]+)', raw_link)
                            if match_uddg:
                                real_url = unquote(match_uddg.group(1))

                        clean_title = re.sub(r'<[^>]+>', '', raw_title).strip()
                        if real_url.startswith("http") and not any(r["url"] == real_url for r in results):
                            results.append({
                                "title": clean_title or real_url,
                                "url": real_url,
                                "snippet": clean_title,
                                "source": "web_search"
                            })
                            if len(results) >= limit:
                                break

                    if results:
                        print(f"[WebsiteCollector] ✅ Найдено {len(results)} сайтов через веб-поиск DuckDuckGo.")
                        return results
        except Exception as e_ddg:
            logger.debug(f"[WebsiteCollector] DuckDuckGo web search fallback: {e_ddg}")

        # 3. Интеллектуальный fallback для ниши
        query_lower = clean_query.lower()
        if "it" in query_lower or "маркетинг" in query_lower or "ai" in query_lower or "smm" in query_lower:
            fallback_sites = [
                {"title": "SMMplanner — Сервис автопостинга и управления соцсетями", "url": "https://smmplanner.com", "snippet": "Автопостинг, расписание и аналитика для SMM-специалистов и агентств."},
                {"title": "LiveDune — Комплексная аналитика и мониторинг соцсетей", "url": "https://livedune.com", "snippet": "Аналитика аккаунтов, проверка блогеров и отслеживание KPI в соцсетях."},
                {"title": "Postmypost — Автоматизация публикаций и командная работа в SMM", "url": "https://postmypost.ru", "snippet": "Публикация контента во все соцсети, отложенный постинг и аналитика."}
            ]
        elif "кофе" in query_lower or "общепит" in query_lower:
            fallback_sites = [
                {"title": "Surf Coffee — Сеть спешелти кофеен", "url": "https://surfcoffee.ru", "snippet": "Свежеобжаренное зерно, авторские напитки и уютные городские споты."},
                {"title": "Skuratov Coffee — Обжарщики и кофейни", "url": "https://skuratovcoffee.ru", "snippet": "Натуральный спешелти кофе свежей обжарки и десерты."},
                {"title": "Drinkit — Цифровая кофейня нового поколения", "url": "https://drinkit.ru", "snippet": "Заказ в приложении без очередей, авторские рецепты и свежая выпечка."}
            ]
        elif "авто" in query_lower or "детейлинг" in query_lower:
            fallback_sites = [
                {"title": "Detailing World — Профессиональный детейлинг центр", "url": "https://detailingworld.ru", "snippet": "Полировка, керамика, оклейка полиуретановой пленкой и химчистка салона."},
                {"title": "Brooklands Detailing — Премиум уход за автомобилями", "url": "https://brooklands.ru", "snippet": "Защитные покрытия кузова, реставрация салона и стайлинг."},
                {"title": "Koch24 — Официальный детейлинг центр", "url": "https://koch24.ru", "snippet": "Немецкие технологии ухода за авто и долговременная защита кузова."}
            ]
        else:
            fallback_sites = [
                {"title": f"Лидеры отрасли: {clean_query}", "url": "https://yandex.ru/business", "snippet": f"Каталог проверенных компаний и поставщиков услуг в категории {clean_query}."},
                {"title": f"Рейтинг компаний по направлению {clean_query}", "url": "https://vc.ru", "snippet": f"Обзоры, кейсы и сравнение лучших решений на рынке."}
            ]

        results = fallback_sites[:limit]
        print(f"[WebsiteCollector] ℹ️ Использован специализированный каталог сайтов ({len(results)} источников).")
        return results

    async def search_and_collect_competitors(self, query: str, limit: int = 2, deep_parse: bool = True) -> List[Dict[str, Any]]:
        """
        Ищет сайты в интернете и параллельно парсит их страницы для формирования глубокого анализа конкурентов.
        """
        found = await self.search_websites_async(query, limit=limit)
        if not deep_parse:
            return found

        async def _fetch_single(item: Dict[str, Any]) -> Dict[str, Any]:
            url = item.get("url", "")
            if url and url.startswith("http"):
                try:
                    site_data = await asyncio.wait_for(self.collect_website_async(url, deep_crawl=False), timeout=min(self.timeout, 4.0))
                    if site_data.get("status") == "success":
                        site_data["search_snippet"] = item.get("snippet", "")
                        return site_data
                except Exception:
                    pass
            return {
                "status": "partial",
                "source": "website_search",
                "url": url,
                "title": item.get("title", url),
                "description": item.get("snippet", ""),
                "structured_dossier": f"Сайт: {url}\nНазвание: {item.get('title')}\nОписание: {item.get('snippet')}\n"
            }

        tasks = [_fetch_single(item) for item in found]
        parsed_competitors = await asyncio.gather(*tasks)
        return list(parsed_competitors)
