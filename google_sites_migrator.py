#!/usr/bin/env python3
"""
Google Sites to GitHub Pages Migrator
======================================
Script reusable para migrar sitios de Google Sites a GitHub Pages.

Usa Playwright para renderizar el JS de Google Sites antes de extraer
contenido (Google Sites moderno renderiza con JavaScript).

Uso:
    python google_sites_migrator.py <URL_BASE> [--output DIR] [--site-title TITULO]

Ejemplo:
    python google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb/EQUIPOS
"""

import sys
import re
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Browser, Page


@dataclass
class PageContent:
    """Contenido extraído de una página"""
    url: str
    title: str
    category: str
    item_id: str
    sections: List[Dict[str, str]] = field(default_factory=list)  # [{title, html}]
    links: List[Dict[str, str]] = field(default_factory=list)
    is_index: bool = False


class GoogleSitesMigrator:
    """Migrador de Google Sites a GitHub Pages (con renderizado JS)"""

    def __init__(self, base_url: str, output_dir: str = "migrated_site", site_title: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.site_title = site_title  # se autocompleta si no se pasa
        self.visited_urls: Set[str] = set()
        self.navigation: Dict[str, List[str]] = {}  # categoria -> [urls]
        self.pages_data: List[PageContent] = []

        parsed = urlparse(self.base_url)
        self.site_origin = f"{parsed.scheme}://{parsed.netloc}"
        # Path base del sitio: ej. /view/qr-groupe-seb
        path_parts = [p for p in parsed.path.split('/') if p]
        # Detectar prefijo del sitio: /view/<site-id>
        if len(path_parts) >= 2 and path_parts[0] == 'view':
            self.site_prefix = f"/view/{path_parts[1]}"
            self.site_id = path_parts[1]
        else:
            self.site_prefix = parsed.path
            self.site_id = path_parts[-1] if path_parts else "site"

        # Playwright lifecycle
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._page: Optional[Page] = None

    # ------------------------------------------------------------------
    # Playwright lifecycle
    # ------------------------------------------------------------------
    def _start_browser(self):
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=True)
        self._page = self._browser.new_page(viewport={"width": 1400, "height": 900})

    def _stop_browser(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._browser = None
        self._page = None
        self._playwright = None

    def fetch_page(self, url: str) -> str:
        """Carga la URL en Chromium headless y devuelve el HTML renderizado."""
        try:
            self._page.goto(url, wait_until="networkidle", timeout=45000)
            # Pequeña espera adicional para asegurar render de contenido dinámico
            self._page.wait_for_timeout(800)
            return self._page.content()
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return ""

    # ------------------------------------------------------------------
    # Extracción
    # ------------------------------------------------------------------
    def _normalize_internal_url(self, href: str) -> Optional[str]:
        """Convierte un href interno a URL absoluta del Google Site, o None si no aplica."""
        if not href:
            return None
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
            return None
        absolute = urljoin(self.base_url + '/', href)
        parsed = urlparse(absolute)
        if parsed.netloc != urlparse(self.base_url).netloc:
            return None
        if not parsed.path.startswith(self.site_prefix):
            return None
        # Limpiar fragmento
        clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')
        return clean

    def _categorize(self, url: str) -> tuple:
        """Devuelve (category, item_id, is_index) a partir de la URL."""
        parsed = urlparse(url)
        path_rel = parsed.path[len(self.site_prefix):].strip('/')
        parts = [unquote(p) for p in path_rel.split('/') if p]
        if not parts:
            return ("home", "index", True)
        if len(parts) == 1:
            return (parts[0], "index", True)
        return (parts[0], parts[-1], False)

    def extract_navigation(self, html: str) -> Dict[str, List[str]]:
        """Extrae enlaces internos del sitio, agrupados por categoría (primer segmento)."""
        soup = BeautifulSoup(html, 'lxml')
        nav: Dict[str, List[str]] = {}

        for a in soup.find_all('a', href=True):
            absolute = self._normalize_internal_url(a['href'])
            if not absolute:
                continue
            category, item_id, is_index = self._categorize(absolute)
            if category == "home":
                continue
            nav.setdefault(category, [])
            if absolute not in nav[category]:
                nav[category].append(absolute)

        return nav

    def _extract_external_links(self, main_soup) -> List[Dict[str, str]]:
        """Extrae links externos (Drive, Docs, externos en general) con texto."""
        links = []
        seen = set()
        for a in main_soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith('http'):
                continue
            if 'sites.google.com' in href:
                continue
            # Google Sites envuelve URLs externas en redirect: /url?q=<real>
            real_href = href
            m = re.search(r'[?&]q=([^&]+)', href)
            if m and 'google.com/url' in href:
                real_href = unquote(m.group(1))
            text = a.get_text(strip=True)
            if not text:
                continue
            key = (text, real_href)
            if key in seen:
                continue
            seen.add(key)
            links.append({"text": text, "url": real_href})
        return links

    def extract_page_content(self, html: str, url: str) -> PageContent:
        """Extrae contenido estructurado de una página (con HTML ya renderizado).

        Google Sites: el h1 (título) está dentro de role='main' pero los h2 y el
        contenido real están en otros contenedores. Buscamos en todo el body y
        filtramos los headings que pertenecen al chrome (header/footer/nav/aside).
        """
        soup = BeautifulSoup(html, 'lxml')

        # Título: primer h1 visible (típicamente dentro de role='main' o del body)
        main_role = soup.find(attrs={'role': 'main'})
        h1 = (main_role.find('h1') if main_role else None) or soup.find('h1')
        title = h1.get_text(strip=True) if h1 else "Sin título"

        def in_chrome(el):
            """True si el elemento está dentro de header/footer/nav/aside (chrome del sitio)."""
            p = el.parent
            while p is not None and p.name != '[document]':
                if p.name in ('header', 'footer', 'nav', 'aside'):
                    return True
                p = p.parent
            return False

        # Secciones: todos los h2 del documento, fuera del chrome.
        # En Google Sites cada bloque está dentro de un <section> y el contenido
        # bajo el h2 vive en divs *hermanos* del div del h2 (no descendientes),
        # así que hay que subir al <section> ancestro para capturarlo.
        sections = []
        seen_sections = set()
        for h2 in soup.find_all('h2'):
            if in_chrome(h2):
                continue
            section_title = h2.get_text(strip=True)
            if not section_title:
                continue
            section_el = h2.find_parent('section')
            if section_el is not None:
                sid = id(section_el)
                if sid in seen_sections:
                    continue
                seen_sections.add(sid)
                full_text = section_el.get_text(' ', strip=True)
            else:
                # Fallback: usar el ancestro tyJCtd o el padre
                box = h2.find_parent(class_='tyJCtd') or h2.parent
                full_text = box.get_text(' ', strip=True) if box else section_title
            content = full_text[len(section_title):].strip() if full_text.startswith(section_title) else full_text
            sections.append({"title": section_title, "content": content})

        # Links externos: buscar en todo el documento (fuera del chrome)
        body_for_links = soup.body or soup
        links = []
        seen = set()
        for a in body_for_links.find_all('a', href=True):
            if in_chrome(a):
                continue
            href = a['href']
            if not href.startswith('http') or 'sites.google.com' in href:
                continue
            real = href
            m = re.search(r'[?&]q=([^&]+)', href)
            if m and 'google.com/url' in href:
                real = unquote(m.group(1))
            text = a.get_text(strip=True)
            if not text:
                continue
            key = (text, real)
            if key in seen:
                continue
            seen.add(key)
            links.append({"text": text, "url": real})

        category, item_id, is_index = self._categorize(url)

        return PageContent(
            url=url,
            title=title,
            category=category,
            item_id=item_id,
            sections=sections,
            links=links,
            is_index=is_index,
        )

    # ------------------------------------------------------------------
    # Scraping
    # ------------------------------------------------------------------
    def scrape_site(self):
        print("🔍 Iniciando escaneo del sitio...")

        main_html = self.fetch_page(self.base_url)
        if not main_html:
            print("❌ No se pudo acceder al sitio base")
            return

        # Autodetectar título del sitio si no se proporcionó
        if not self.site_title:
            soup = BeautifulSoup(main_html, 'lxml')
            # Google Sites pone el nombre del sitio en el header (h1 dentro del banner top)
            header = soup.find('header')
            header_h1 = header.find('h1') if header else None
            if header_h1 and header_h1.get_text(strip=True):
                self.site_title = header_h1.get_text(strip=True)
            else:
                # Fallback: derivar del site_id preservando mayúsculas frecuentes
                parts = self.site_id.split('-')
                # Si la parte parece una sigla (≤3 letras), mantenerla en mayúsculas
                self.site_title = ' '.join(
                    p.upper() if len(p) <= 3 else p.capitalize() for p in parts
                )

        self.navigation = self.extract_navigation(main_html)
        print(f"📁 Categorías encontradas: {list(self.navigation.keys())}")
        print(f"🏷️  Título del sitio: {self.site_title}")

        # Procesar todas las URLs descubiertas (también las páginas índice de categoría)
        all_urls = [self.base_url]
        for cat, urls in self.navigation.items():
            for u in urls:
                if u not in all_urls:
                    all_urls.append(u)

        print(f"📄 Total de páginas a procesar: {len(all_urls)}")

        for i, url in enumerate(all_urls, 1):
            if url in self.visited_urls:
                continue
            print(f"[{i}/{len(all_urls)}] {url}")
            html = self.fetch_page(url)
            if not html:
                continue
            page_content = self.extract_page_content(html, url)
            self.pages_data.append(page_content)
            self.visited_urls.add(url)

            # Descubrir más páginas desde esta (por si la nav del root no tenía todas)
            sub_nav = self.extract_navigation(html)
            for cat, urls in sub_nav.items():
                self.navigation.setdefault(cat, [])
                for u in urls:
                    if u not in self.navigation[cat]:
                        self.navigation[cat].append(u)
                    if u not in all_urls and u not in self.visited_urls:
                        all_urls.append(u)

        print(f"✅ Escaneo completado. {len(self.pages_data)} páginas extraídas.")

    # ------------------------------------------------------------------
    # Generación HTML
    # ------------------------------------------------------------------
    def _relative_path(self, target_rel: str, from_depth: int) -> str:
        """Devuelve un path relativo desde un archivo a profundidad `from_depth` hasta `target_rel` (relativo al root del output)."""
        if from_depth == 0:
            return target_rel
        return '../' * from_depth + target_rel

    def _html_template(self) -> str:
        return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#0969da">
    <title>{title} — {site_title}</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
    <div class="sidebar-backdrop" aria-hidden="true"></div>
    <header class="topbar">
        <button class="menu-toggle" aria-label="Abrir menú" aria-controls="sidebar" aria-expanded="false">☰</button>
        <span class="topbar-title">{title}</span>
    </header>
    <div class="layout">
        <aside class="sidebar" id="sidebar">
            <div class="brand">
                <a href="{home_path}">
                    <h1>{site_title}</h1>
                </a>
                <button class="sidebar-close" aria-label="Cerrar menú">✕</button>
            </div>
            {navigation}
            <div class="sidebar-footer">
                <a href="{source_url}" target="_blank" rel="noopener">Sitio original ↗</a>
            </div>
        </aside>
        <main class="content">
            <article>
                {content}
            </article>
        </main>
    </div>
    <script src="{js_path}"></script>
</body>
</html>
"""

    def _build_nav_html(self, from_depth: int, current_url: str) -> str:
        """Construye la navegación con paths relativos según profundidad."""
        out = ['<nav class="nav"><ul class="nav-list">']
        for category, urls in self.navigation.items():
            cat_index_target = f"{category.lower()}/index.html"
            cat_path = self._relative_path(cat_index_target, from_depth)
            out.append('<li class="nav-group">')
            out.append('<div class="nav-cat-row">')
            out.append(f'<button class="nav-cat" aria-expanded="false">{category}</button>')
            out.append('</div>')
            out.append(f'<a class="nav-cat-link" href="{cat_path}">Ver categoría completa →</a>')
            out.append('<ul class="nav-items">')
            items = []
            for u in urls:
                page = next((p for p in self.pages_data if p.url == u), None)
                if not page or page.is_index:
                    continue
                items.append(page)
            items.sort(key=lambda p: p.item_id)
            for page in items:
                target = f"{page.category.lower()}/{page.item_id}.html"
                rel = self._relative_path(target, from_depth)
                active = ' class="active"' if page.url == current_url else ''
                out.append(f'<li><a{active} href="{rel}">{page.item_id}</a></li>')
            out.append('</ul></li>')
        out.append('</ul></nav>')
        return '\n'.join(out)

    def _render_page_body(self, page: PageContent) -> str:
        parts = [f'<header class="page-header"><h1>{page.title}</h1>']
        parts.append(f'<p class="breadcrumb"><a href="../index.html">Inicio</a> / <a href="index.html">{page.category}</a> / <span>{page.item_id}</span></p>')
        parts.append('</header>')

        if page.sections:
            parts.append('<div class="accordion">')
            for sec in page.sections:
                content = sec.get('content', '').strip()
                parts.append('<div class="acc-item">')
                parts.append(
                    f'<button class="acc-header" aria-expanded="false">'
                    f'<span class="acc-title">{sec["title"]}</span>'
                    f'<span class="acc-chevron" aria-hidden="true">›</span></button>'
                )
                parts.append('<div class="acc-body">')
                if content:
                    for para in content.split('\n'):
                        para = para.strip()
                        if para:
                            parts.append(f'<p>{para}</p>')
                else:
                    parts.append('<p class="empty">Sin datos.</p>')
                parts.append('</div></div>')
            parts.append('</div>')
        else:
            parts.append('<p class="empty">Esta página no tiene secciones extraídas.</p>')

        if page.links:
            parts.append('<section class="external-links">')
            parts.append('<h2>Documentos y enlaces</h2>')
            parts.append('<ul class="link-list">')
            for link in page.links:
                parts.append(f'<li><a class="link-btn" href="{link["url"]}" target="_blank" rel="noopener">{link["text"]} ↗</a></li>')
            parts.append('</ul></section>')

        return '\n'.join(parts)

    def _render_category_index(self, category: str) -> str:
        pages = [p for p in self.pages_data if p.category.lower() == category.lower() and not p.is_index]
        pages.sort(key=lambda p: p.item_id)
        out = [f'<header class="page-header"><h1>{category}</h1>']
        out.append(f'<p class="breadcrumb"><a href="../index.html">Inicio</a> / <span>{category}</span></p>')
        out.append(f'<p class="count">{len(pages)} elementos</p></header>')
        out.append('<div class="accordion">')
        for p in pages:
            link = f"{p.item_id}.html"
            # Preview: primeras 2-3 secciones con contenido
            preview_rows = []
            for s in p.sections[:3]:
                content = s.get('content', '').strip()
                if not content:
                    continue
                preview_rows.append(
                    f'<div class="acc-row"><span class="acc-row-label">{s["title"]}</span>'
                    f'<span class="acc-row-value">{content[:120]}</span></div>'
                )
            preview_html = ''.join(preview_rows) if preview_rows else '<p class="empty">Sin datos previos disponibles.</p>'
            out.append('<div class="acc-item">')
            out.append(f'<button class="acc-header" aria-expanded="false">'
                       f'<span class="acc-title">{p.item_id}</span>'
                       f'<span class="acc-meta">{p.title if p.title != p.item_id else ""}</span>'
                       f'<span class="acc-chevron" aria-hidden="true">›</span></button>')
            out.append(f'<div class="acc-body">{preview_html}'
                       f'<a class="acc-cta" href="{link}">Ver ficha completa →</a></div>')
            out.append('</div>')
        out.append('</div>')
        return '\n'.join(out)

    def _render_home(self) -> str:
        out = [f'<header class="page-header"><h1>{self.site_title}</h1>']
        out.append('<p class="subtitle">Documentación técnica</p></header>')
        out.append('<div class="accordion">')
        for category, urls in self.navigation.items():
            items = [p for p in self.pages_data if p.category.lower() == category.lower() and not p.is_index]
            items.sort(key=lambda p: p.item_id)
            cat_link = f"{category.lower()}/index.html"
            out.append('<div class="acc-item">')
            out.append(f'<button class="acc-header" aria-expanded="false">'
                       f'<span class="acc-title">{category}</span>'
                       f'<span class="acc-meta">{len(items)} elementos</span>'
                       f'<span class="acc-chevron" aria-hidden="true">›</span></button>')
            out.append('<div class="acc-body">')
            out.append('<ul class="acc-list">')
            for p in items:
                out.append(f'<li><a href="{p.category.lower()}/{p.item_id}.html">{p.item_id}</a></li>')
            out.append('</ul>')
            out.append(f'<a class="acc-cta" href="{cat_link}">Ver categoría completa →</a>')
            out.append('</div></div>')
        out.append('</div>')
        return '\n'.join(out)

    def generate_static_site(self):
        print("🏗️  Generando sitio estático...")
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "styles.css").write_text(self.generate_css(), encoding='utf-8')
        (self.output_dir / "script.js").write_text(self.generate_javascript(), encoding='utf-8')
        print("✅ styles.css + script.js generados")

        template = self._html_template()

        # Index home (depth 0)
        nav_html = self._build_nav_html(from_depth=0, current_url=self.base_url)
        home_html = template.format(
            title="Inicio",
            site_title=self.site_title,
            css_path="styles.css",
            js_path="script.js",
            home_path="index.html",
            source_url=self.base_url,
            navigation=nav_html,
            content=self._render_home(),
        )
        (self.output_dir / "index.html").write_text(home_html, encoding='utf-8')
        print("✅ index.html generado")

        # Páginas por categoría
        for category in self.navigation.keys():
            cat_dir = self.output_dir / category.lower()
            cat_dir.mkdir(exist_ok=True)
            # Index de categoría (depth 1)
            nav_html_cat = self._build_nav_html(from_depth=1, current_url=f"{self.base_url}/{category}")
            cat_index_html = template.format(
                title=category,
                site_title=self.site_title,
                css_path="../styles.css",
                js_path="../script.js",
                home_path="../index.html",
                source_url=f"{self.site_origin}{self.site_prefix}/{category}",
                navigation=nav_html_cat,
                content=self._render_category_index(category),
            )
            (cat_dir / "index.html").write_text(cat_index_html, encoding='utf-8')

        # Páginas individuales
        item_pages = [p for p in self.pages_data if not p.is_index]
        for page in item_pages:
            cat_dir = self.output_dir / page.category.lower()
            cat_dir.mkdir(exist_ok=True)
            nav_html_item = self._build_nav_html(from_depth=1, current_url=page.url)
            page_html = template.format(
                title=page.title,
                site_title=self.site_title,
                css_path="../styles.css",
                js_path="../script.js",
                home_path="../index.html",
                source_url=page.url,
                navigation=nav_html_item,
                content=self._render_page_body(page),
            )
            (cat_dir / f"{page.item_id}.html").write_text(page_html, encoding='utf-8')

        print(f"✅ {len(item_pages)} páginas + {len(self.navigation)} índices de categoría generadas")

    # ------------------------------------------------------------------
    # CSS + JS
    # ------------------------------------------------------------------
    def generate_css(self) -> str:
        return """:root {
    --bg: #ffffff;
    --bg-alt: #f6f8fa;
    --border: #e1e4e8;
    --text: #1f2328;
    --text-muted: #57606a;
    --accent: #0969da;
    --accent-hover: #0550ae;
    --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-hover: 0 4px 12px rgba(0,0,0,0.08);
    --radius: 8px;
    --topbar-h: 56px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { -webkit-text-size-adjust: 100%; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
    -webkit-tap-highlight-color: rgba(9,105,218,0.15);
}

.layout { display: grid; grid-template-columns: 280px 1fr; min-height: 100vh; }

/* ---------------- Topbar (sólo móvil) ---------------- */
.topbar {
    display: none;
    position: sticky;
    top: 0;
    z-index: 8;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    height: var(--topbar-h);
    align-items: center;
    padding: 0 12px;
    gap: 8px;
}
.topbar .topbar-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.menu-toggle {
    display: none;
    background: transparent;
    border: 0;
    width: 44px;
    height: 44px;
    font-size: 22px;
    cursor: pointer;
    border-radius: var(--radius);
    color: var(--text);
    line-height: 1;
}
.menu-toggle:hover { background: var(--bg-alt); }

.sidebar-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.45);
    z-index: 9;
    opacity: 0;
    transition: opacity 0.2s ease;
}
.sidebar-backdrop.show { display: block; opacity: 1; }

/* ---------------- Sidebar ---------------- */
.sidebar {
    background: var(--bg-alt);
    border-right: 1px solid var(--border);
    padding: 24px 0;
    overflow-y: auto;
    position: sticky;
    top: 0;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.brand { padding: 0 24px 20px; border-bottom: 1px solid var(--border); }
.brand a { color: var(--text); text-decoration: none; }
.brand h1 { font-size: 18px; font-weight: 600; letter-spacing: -0.01em; }

.sidebar-close {
    display: none;
    background: transparent;
    border: 0;
    width: 40px;
    height: 40px;
    font-size: 20px;
    cursor: pointer;
    border-radius: 6px;
    color: var(--text-muted);
    line-height: 1;
}
.sidebar-close:hover { background: rgba(0,0,0,0.06); color: var(--text); }

.nav { flex: 1; padding: 12px 12px 8px; }
.nav-list { list-style: none; }
.nav-group { margin-bottom: 6px; }

.nav-cat-row {
    display: flex;
    align-items: center;
    gap: 4px;
}
.nav-cat {
    flex: 1;
    text-align: left;
    background: none;
    border: 0;
    padding: 10px 12px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    cursor: pointer;
    border-radius: 6px;
    font-family: inherit;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.nav-cat::after {
    content: "›";
    transform: rotate(90deg);
    transition: transform 0.2s ease;
    font-size: 18px;
    margin-left: 8px;
    color: var(--text-muted);
}
.nav-group.open .nav-cat::after { transform: rotate(-90deg); }
.nav-cat:hover { background: rgba(9,105,218,0.08); color: var(--accent); }

.nav-cat-link {
    padding: 4px 12px 8px;
    font-size: 11px;
    color: var(--accent);
    text-decoration: none;
    display: block;
}
.nav-cat-link:hover { text-decoration: underline; }

.nav-items {
    list-style: none;
    padding-left: 6px;
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.25s ease;
}
.nav-group.open .nav-items { max-height: 6000px; }
.nav-items li a {
    display: block;
    padding: 10px 12px;
    font-size: 14px;
    color: var(--text);
    text-decoration: none;
    border-radius: 6px;
    border-left: 2px solid transparent;
    margin-bottom: 2px;
}
.nav-items li a:hover { background: rgba(9,105,218,0.08); color: var(--accent); }
.nav-items li a.active {
    background: rgba(9,105,218,0.12);
    color: var(--accent);
    border-left-color: var(--accent);
    font-weight: 600;
}

.sidebar-footer {
    padding: 16px 24px;
    border-top: 1px solid var(--border);
    font-size: 12px;
}
.sidebar-footer a { color: var(--text-muted); text-decoration: none; }
.sidebar-footer a:hover { color: var(--accent); }

/* ---------------- Content ---------------- */
.content { padding: 48px 56px; max-width: 960px; }
.page-header { margin-bottom: 32px; padding-bottom: 24px; border-bottom: 1px solid var(--border); }
.page-header h1 {
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
    word-break: break-word;
}
.page-header .subtitle { color: var(--text-muted); font-size: 16px; }
.page-header .count { color: var(--text-muted); font-size: 14px; margin-top: 4px; }

.breadcrumb { font-size: 13px; color: var(--text-muted); }
.breadcrumb a { color: var(--accent); text-decoration: none; }
.breadcrumb a:hover { text-decoration: underline; }
.breadcrumb span { color: var(--text); }

.info-section {
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 16px;
}
.info-section h2 {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
}
.info-section p { font-size: 15px; color: var(--text); margin-bottom: 4px; }
.info-section .empty { color: var(--text-muted); font-style: italic; }

.external-links {
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
}
.external-links h2 { font-size: 18px; margin-bottom: 16px; }
.link-list { list-style: none; display: flex; flex-wrap: wrap; gap: 12px; }
.link-btn {
    display: inline-flex;
    align-items: center;
    min-height: 44px;
    padding: 12px 20px;
    background: var(--accent);
    color: white;
    text-decoration: none;
    border-radius: var(--radius);
    font-size: 15px;
    font-weight: 500;
    transition: background 0.15s ease;
}
.link-btn:hover, .link-btn:active { background: var(--accent-hover); }

/* ---------------- Acordeones (cards colapsables) ---------------- */
.accordion {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 16px;
}

.acc-item {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    overflow: hidden;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.acc-item:hover { border-color: var(--accent); }
.acc-item.open { box-shadow: var(--shadow-hover); }

.acc-header {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 16px 18px;
    background: transparent;
    border: 0;
    cursor: pointer;
    text-align: left;
    font-family: inherit;
    color: var(--text);
    min-height: 56px;
}
.acc-header:hover { background: var(--bg-alt); }

.acc-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    flex: 1;
}
.acc-meta {
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 400;
    margin-right: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 50%;
}
.acc-chevron {
    font-size: 22px;
    line-height: 1;
    color: var(--text-muted);
    transition: transform 0.2s ease;
    flex-shrink: 0;
}
.acc-item.open .acc-chevron { transform: rotate(90deg); color: var(--accent); }

.acc-body {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
    padding: 0 18px;
    border-top: 1px solid transparent;
}
.acc-item.open .acc-body {
    max-height: 4000px;
    padding: 14px 18px 18px;
    border-top-color: var(--border);
}

.acc-row {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}
.acc-row:last-of-type { border-bottom: 0; }
.acc-row-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.acc-row-value { font-size: 14px; color: var(--text); }

.acc-list {
    list-style: none;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 6px;
    margin-bottom: 14px;
}
.acc-list li a {
    display: block;
    padding: 8px 10px;
    background: var(--bg-alt);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    text-align: center;
    transition: background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
}
.acc-list li a:hover, .acc-list li a:active {
    background: rgba(9,105,218,0.08);
    border-color: var(--accent);
    color: var(--accent);
}

.acc-cta {
    display: inline-block;
    margin-top: 8px;
    color: var(--accent);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
}
.acc-cta:hover { text-decoration: underline; }

.acc-body .empty {
    color: var(--text-muted);
    font-style: italic;
    font-size: 13px;
    padding: 4px 0 8px;
}
.acc-body p {
    font-size: 15px;
    color: var(--text);
    margin-bottom: 6px;
    line-height: 1.5;
}
.acc-body p:last-child { margin-bottom: 0; }

/* ---------------- Mobile (<= 900px) ---------------- */
@media (max-width: 900px) {
    .layout { grid-template-columns: 1fr; }

    .topbar { display: flex; }
    .menu-toggle { display: flex; align-items: center; justify-content: center; }

    .sidebar {
        position: fixed;
        top: 0; left: 0;
        width: min(86vw, 320px);
        height: 100dvh;
        z-index: 10;
        transform: translateX(-100%);
        transition: transform 0.25s ease;
        padding: 16px 0 12px;
        box-shadow: 4px 0 16px rgba(0,0,0,0.08);
    }
    .sidebar.open { transform: translateX(0); }

    .brand {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 16px 16px;
    }
    .brand h1 { font-size: 17px; }
    .sidebar-close { display: flex; align-items: center; justify-content: center; }

    .nav-items li a { padding: 12px 14px; font-size: 15px; }

    .content {
        padding: 20px 16px 40px;
        max-width: 100%;
    }
    .page-header { margin-bottom: 20px; padding-bottom: 16px; }
    .page-header h1 { font-size: 26px; }
    .page-header .subtitle { font-size: 15px; }

    .breadcrumb { font-size: 14px; margin-top: 4px; }

    .info-section { padding: 14px 16px; margin-bottom: 10px; }
    .info-section h2 { font-size: 12px; }
    .info-section p { font-size: 15px; }

    .accordion { gap: 6px; margin-top: 12px; }
    .acc-header { padding: 14px 14px; min-height: 56px; }
    .acc-title { font-size: 15px; }
    .acc-meta { font-size: 12px; max-width: 45%; }
    .acc-item.open .acc-body { padding: 12px 14px 14px; }
    .acc-list { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 6px; }
    .acc-list li a { padding: 10px 8px; font-size: 13px; min-height: 38px; display: flex; align-items: center; justify-content: center; }

    .external-links { margin-top: 24px; padding-top: 18px; }
    .link-list { flex-direction: column; gap: 10px; }
    .link-btn { width: 100%; justify-content: center; font-size: 16px; }
}

@media (max-width: 380px) {
    .page-header h1 { font-size: 22px; }
    .acc-meta { display: none; }
}
"""

    def generate_javascript(self) -> str:
        return """document.addEventListener('DOMContentLoaded', function () {
    var sidebar = document.querySelector('.sidebar');
    var backdrop = document.querySelector('.sidebar-backdrop');
    var toggle = document.querySelector('.menu-toggle');
    var closeBtn = document.querySelector('.sidebar-close');

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add('open');
        if (backdrop) backdrop.classList.add('show');
        if (toggle) toggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }
    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove('open');
        if (backdrop) backdrop.classList.remove('show');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    if (toggle) toggle.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (backdrop) backdrop.addEventListener('click', closeSidebar);

    // Cerrar al navegar (en móvil)
    document.querySelectorAll('.sidebar a').forEach(function (a) {
        a.addEventListener('click', function () {
            if (window.matchMedia('(max-width: 900px)').matches) closeSidebar();
        });
    });

    // Cerrar con tecla Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeSidebar();
    });

    // Toggle de categorías
    document.querySelectorAll('.nav-cat').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var group = btn.closest('.nav-group');
            var open = group.classList.toggle('open');
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    });

    // Abrir automáticamente la categoría con link activo (o todas si no hay activo)
    var active = document.querySelector('.nav-items a.active');
    if (active) {
        var group = active.closest('.nav-group');
        if (group) {
            group.classList.add('open');
            var b = group.querySelector('.nav-cat');
            if (b) b.setAttribute('aria-expanded', 'true');
        }
    } else {
        document.querySelectorAll('.nav-group').forEach(function (g) {
            g.classList.add('open');
            var b = g.querySelector('.nav-cat');
            if (b) b.setAttribute('aria-expanded', 'true');
        });
    }

    // Scroll al ítem activo dentro del sidebar
    if (active) {
        setTimeout(function () {
            active.scrollIntoView({ block: 'center', behavior: 'instant' });
        }, 30);
    }

    // Acordeones de contenido (cards colapsables)
    document.querySelectorAll('.acc-header').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var item = btn.closest('.acc-item');
            if (!item) return;
            var open = item.classList.toggle('open');
            btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    });
});
"""

    # ------------------------------------------------------------------
    # GitHub Pages artifacts + metadata
    # ------------------------------------------------------------------
    def generate_github_files(self):
        readme = f"""# {self.site_title}

Sitio migrado automáticamente desde: {self.base_url}

## Deploy a GitHub Pages

```bash
git init && git add . && git commit -m "Initial commit"
gh repo create {self.site_id} --public --source=. --remote=origin --push
# Luego en GitHub: Settings → Pages → Source: main / (root)
```

URL final: `https://<usuario>.github.io/{self.site_id}/`

## Migración

- **Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Páginas:** {len(self.pages_data)}
- **Categorías:** {len(self.navigation)}
"""
        (self.output_dir / "README.md").write_text(readme, encoding='utf-8')
        (self.output_dir / ".gitignore").write_text(
            "__pycache__/\n.DS_Store\nThumbs.db\n.vscode/\n.idea/\n",
            encoding='utf-8',
        )
        # .nojekyll para que GitHub Pages no procese con Jekyll (importante si hubiera carpetas _xxx)
        (self.output_dir / ".nojekyll").write_text("", encoding='utf-8')
        print("✅ README.md + .gitignore + .nojekyll generados")

    def save_metadata(self):
        metadata = {
            "source_url": self.base_url,
            "site_title": self.site_title,
            "site_id": self.site_id,
            "migration_date": datetime.now().isoformat(),
            "pages_migrated": len(self.pages_data),
            "categories": list(self.navigation.keys()),
            "pages": [asdict(p) for p in self.pages_data],
        }
        (self.output_dir / "migration_metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        print("✅ migration_metadata.json generado")

    # ------------------------------------------------------------------
    def run(self):
        print("=" * 60)
        print("🚀 GOOGLE SITES TO GITHUB PAGES MIGRATOR")
        print("=" * 60)
        print(f"📍 URL Base: {self.base_url}")
        print(f"📁 Salida: {self.output_dir}")
        print("=" * 60)
        try:
            self._start_browser()
            self.scrape_site()
            print()
            self.generate_static_site()
            self.generate_github_files()
            self.save_metadata()
        finally:
            self._stop_browser()

        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA")
        print("=" * 60)
        print(f"📂 {self.output_dir.absolute()}")
        print("\n📝 Para deploy:")
        print(f"  cd {self.output_dir}")
        print("  git init && git add . && git commit -m 'Sitio migrado'")
        print(f"  gh repo create {self.site_id} --public --source=. --remote=origin --push")


def main():
    parser = argparse.ArgumentParser(
        description="Migra un Google Site a GitHub Pages (con renderizado JS)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('url', help='URL base del Google Site')
    parser.add_argument('--output', '-o', default='migrated_site', help='Directorio de salida')
    parser.add_argument('--site-title', default=None, help='Título del sitio (autodetectado si se omite)')
    args = parser.parse_args()

    if 'sites.google.com' not in args.url:
        print("❌ Error: La URL debe ser de Google Sites")
        sys.exit(1)

    migrator = GoogleSitesMigrator(args.url, args.output, site_title=args.site_title)
    migrator.run()


if __name__ == "__main__":
    main()
