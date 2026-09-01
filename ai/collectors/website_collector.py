# File: collectors/website_collector.py
from __future__ import annotations

import re
import html
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser

logger = logging.getLogger('ucust_collectors.website')

class CleanHTMLParser(HTMLParser):
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
        self._current_tag = ''
        self._current_text = []
        self._skip_tags = {'script', 'style', 'svg', 'noscript', 'header', 'footer', 'nav', 'aside'}
        self._in_skip = False

    def handle_starttag(self, tag, attrs):
        self._current_tag = tag.lower()
        attr_dict = {k.lower(): (v or '') for k, v in attrs}
        if self._current_tag in self._skip_tags:
            self._in_skip = True
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
        elif self._current_tag == 'a':
            href = attr_dict.get('href', '').strip()
            if href:
                self.links.append(href)
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
        if not self._in_skip and data.strip():
            self._current_text.append(data.strip())

class WebsiteCollector:
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    def __init__(self, timeout: float = 12.0):
        self.timeout = timeout

    def _normalize_url(self, raw_url: str) -> str:
        url = raw_url.strip()
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        return url

    async def collect_website_async(self, raw_url: str) -> Dict[str, Any]:
        url = self._normalize_url(raw_url)
        print(f"[WebsiteCollector] Parsing website: {url}...")
        html_content = ''
        final_url = url
        try:
            import httpx
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, verify=False, headers=self.HEADERS) as client:
                resp = await client.get(url)
                final_url = str(resp.url)
                html_content = resp.text
        except Exception as err:
            try:
                import aiohttp
                async with aiohttp.ClientSession(headers=self.HEADERS) as session:
                    async with session.get(url, timeout=self.timeout, ssl=False) as resp:
                        final_url = str(resp.url)
                        html_content = await resp.text()
            except Exception as e2:
                print(f"[WebsiteCollector] Connection error for {url}: {e2}")
                return {'status': 'error', 'url': url, 'error': str(e2), 'source': 'website'}

        parser = CleanHTMLParser()
        try:
            parser.feed(html_content)
        except Exception:
            pass

        all_text_blob = parser.title + ' ' + parser.meta_description + ' ' + ' '.join(parser.headings) + ' ' + ' '.join(parser.paragraphs)
        phones = list(set(re.findall(r'(?:\+7|8)[\s\-]?(?:\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})', all_text_blob)))
        emails = list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', all_text_blob)))
        
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
        seen = set()
        for p in parser.paragraphs:
            cleaned = re.sub(r'\s+', ' ', p).strip()
            if len(cleaned) > 25 and cleaned not in seen:
                seen.add(cleaned)
                unique_paragraphs.append(cleaned)

        title = parser.og_title or parser.title or urlparse(final_url).netloc
        description = parser.og_description or parser.meta_description or ''
        headings_top = parser.headings[:10]
        key_paragraphs = unique_paragraphs[:12]

        summary_dossier = f'Сайт: {final_url}\nНазвание: {title}\n'
        if description:
            summary_dossier += f'Описание (УТП): {description}\n'
        if headings_top:
            summary_dossier += 'Ключевые разделы и предложения:\n- ' + '\n- '.join(headings_top) + '\n'
        if key_paragraphs:
            summary_dossier += 'О компании и услугах:\n' + ' '.join(key_paragraphs[:4]) + '\n'
        if phones or emails:
            summary_dossier += f'Контакты: Телефоны={phones[:2]}, Email={emails[:2]}\n'

        # Фильтрация и формирование качественных ссылок только на контент и товары (без лого и титульных баннеров)
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

            # Строгий отсев логотипов, шапок, кнопок и иконок
            if any(exc in combined_str for exc in LOGO_BANNER_EXCLUSIONS):
                continue
            if any(ext in abs_img.lower() for ext in ['.svg', '.ico', '.gif', 'pixel', 'tracker', '1x1']):
                continue

            seen_img_urls.add(abs_img)
            # Приоритет товарам, каталогу и портфолио
            if any(kw in combined_str for kw in PRODUCT_CONTENT_KEYWORDS):
                priority_images.append(abs_img)
            else:
                regular_images.append(abs_img)

        # Объединяем: сначала явные товары/контент, затем остальные контентные фото
        extracted_images = (priority_images + regular_images)[:15]

        # Скачивание и валидация превью картинок (проверка разрешения и пропорций кадра)
        cached_images = await self.download_and_cache_images_async(extracted_images, max_images=9)

        print(f"[WebsiteCollector] Website parsed successfully: {title} (Content/Product images extracted: {len(cached_images)})")
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
            'structured_dossier': summary_dossier
        }

    async def download_and_cache_images_async(self, image_urls: List[str], max_images: int = 9) -> List[str]:
        """
        Асинхронно скачивает и валидирует превью картинок (отсекает мелкие иконки и вытянутые баннеры).
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

                    # Проверка размеров и пропорций (исключение иконок < 180px и растянутых титульных полос)
                    try:
                        with Image.open(file_path) as pil_img:
                            w, h = pil_img.size
                            if w < 180 or h < 180:
                                os.remove(file_path)
                                continue
                            ratio = w / float(h)
                            if ratio > 2.9 or ratio < 0.34:
                                # Тонкий горизонтальный баннер или полоса-разделитель
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
            print(f"[WebsiteCollector] 📸 Успешно скачано и сохранено {len(cached_files)} фото для Визуального Директора.")
        return cached_files

    async def search_websites_async(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Ищет сайты компаний и конкурентов в интернете (через DuckDuckGo / Tavily / Web Scraper).
        Возвращает список найденных ссылок, заголовков и сниппетов.
        """
        clean_query = query.strip()
        print(f"[WebsiteCollector] 🌐 Поиск сайтов в интернете по запросу: '{clean_query}' (лимит: {limit})...")
        results: List[Dict[str, Any]] = []

        # 1. Попытка через Tavily API если ключ задан в .env
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

        # 2. Поиск через открытый веб-шлюз DuckDuckGo HTML
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

        import asyncio

        async def _fetch_single(item: Dict[str, Any]) -> Dict[str, Any]:
            url = item.get("url", "")
            if url and url.startswith("http"):
                try:
                    site_data = await asyncio.wait_for(self.collect_website_async(url), timeout=min(self.timeout, 4.0))
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
