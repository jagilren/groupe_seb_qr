# CLAUDE.md

Guía para Claude Code cuando trabaje en este repositorio.

## Objetivo principal

Generar una **carpeta de sitio estático** (HTML + CSS + JS) lista para:
- **Opción A:** Subirla a un repo de GitHub y activar GitHub Pages.
- **Opción B:** Importarla a cualquier hosting estático (Netlify, Vercel, S3) o servir local con `python3 -m http.server`.

El input es la URL **raíz** de un Google Site (`https://sites.google.com/view/<site-id>`). El output es una carpeta autosuficiente que no requiere build step ni servidor.

## Stack actual

- **Python 3.12** (probado en WSL Ubuntu 24)
- **Playwright + Chromium headless** — para renderizar el JS de Google Sites antes de scrapear
- **BeautifulSoup + lxml** — para parsear el DOM ya renderizado
- **CSS/JS vainilla** en el sitio generado (sin framework, sin build)

## Setup (estado actual real)

`setup.sh` y `requirements.txt` **están desactualizados** — no instalan Playwright ni Chromium. Hasta que se actualicen, el setup manual es:

```bash
# 1. Dependencias Python (PEP 668 en Ubuntu 24 requiere --break-system-packages)
pip3 install --break-system-packages playwright beautifulsoup4 lxml requests

# 2. Navegador Chromium para Playwright
~/.local/bin/playwright install chromium

# 3. Libs nativas del sistema que Chromium necesita (sudo, una sola vez)
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64
```

`requests` está en `requirements.txt` pero ya no se usa — `fetch_page()` usa Playwright. Se puede eliminar.

## Flujo end-to-end

```bash
# Generar sitio
python3 google_sites_migrator.py <URL_GOOGLE_SITE> --output mi_sitio
# Tarda ~3-4 minutos para 60 páginas (Playwright renderiza c/u con networkidle + 800ms)

# Ver local antes de subir
cd mi_sitio && python3 -m http.server 8000
# Desde WSL → abrir en Chrome de Windows: cmd.exe /c start http://localhost:8000/

# Deploy a GitHub Pages (requiere gh CLI autenticado, o usar git push manual)
cd mi_sitio
git init && git add . && git commit -m "Sitio migrado"
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
# Luego en GitHub: Settings → Pages → Source: main / (root) → Save
```

Ejemplo canónico (sitio de pruebas QR Groupe SEB, planta industrial Medellín):
```bash
python3 google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb --output qr-groupe-seb
```
**Importante:** usar la URL raíz del sitio (`.../view/<site-id>`), **no** una categoría — para que `extract_navigation()` descubra todas las categorías desde el menú del sitio.

## Estructura del output generado

```
mi_sitio/
├── index.html                  # Home: acordeones por categoría
├── styles.css                  # CSS mobile-first con acordeones .acc-item
├── script.js                   # Sidebar overlay + acordeones + scroll-to-active
├── README.md                   # Instrucciones de deploy (auto-generado)
├── .gitignore
├── .nojekyll                   # Evita procesamiento Jekyll en GitHub Pages
├── migration_metadata.json     # Trazabilidad: URL, fecha, páginas, secciones, links
└── <categoria>/                # Una carpeta por categoría descubierta
    ├── index.html              # Índice: acordeones por item con preview
    └── <item_id>.html          # Ficha individual: secciones colapsables
```

Todos los paths son **relativos** (`../styles.css`, `equipos/800-P-01.html`) — funciona tanto en GitHub Pages bajo `/<repo>/` como en cualquier subdirectorio.

## Arquitectura del migrador

Un solo módulo: [google_sites_migrator.py](google_sites_migrator.py). Clase `GoogleSitesMigrator`. Lifecycle Playwright en `_start_browser()` / `_stop_browser()` invocados desde `run()`.

Pipeline:
1. `_start_browser()` — lanza Chromium headless, reusa una `Page` para todas las URLs
2. `scrape_site()` — fetch + recorrido de páginas vinculadas (descubre más URLs en cada hop)
3. `fetch_page(url)` — `page.goto(networkidle)` + 800ms extra de wait, devuelve HTML renderizado
4. `extract_navigation(html)` — descubre categorías dinámicamente desde links internos (primer segmento del path tras `/view/<site-id>/`)
5. `extract_page_content(html, url)` — extrae h1 (título), h2 (secciones) y links externos
6. `generate_static_site()` — escribe HTML por categoría usando `_html_template()` + acordeones
7. `generate_github_files()` + `save_metadata()` — README, .gitignore, .nojekyll, JSON
8. `_stop_browser()` — cierra Playwright

Datos en memoria: `List[PageContent]` (dataclass con `url, title, category, item_id, sections, links, is_index`).

### Hallazgos no obvios sobre Google Sites (importantes si tocas el extractor)

- **`role='main'` solo contiene el `<h1>` del título de la página** — no los h2 ni el contenido. Por eso `extract_page_content()` busca h1 en `role='main'` pero los h2 los busca en `soup.find_all('h2')` filtrando los que están dentro de `<header>/<footer>/<nav>/<aside>` (chrome del site).
- **Los acordeones de Google Sites NO necesitan click para extraer contenido.** El contenido está siempre en el DOM, solo oculto visualmente con CSS. BeautifulSoup lo ve sin problema. Esto es contraintuitivo — descubrirlo me costó varias iteraciones.
- **El contenido bajo cada h2 está en un `<div>` *hermano* del div del h2**, no descendiente. Ambos viven dentro de un `<section class="yaqOZd">` común. Por eso el extractor sube a `h2.find_parent('section')` y toma el texto completo de la sección.
- **Links externos vienen envueltos en redirect** `https://www.google.com/url?q=<real_url>&...`. El extractor desempaqueta el parámetro `q` para mostrar la URL real.
- **Capitalización del site title:** se autodetecta del `<header>/<h1>` del banner top del Google Site. Fallback: deriva del site-id pero **preserva siglas ≤3 letras en mayúsculas** (ej. `qr-groupe-seb` → `QR Groupe Seb`, no `Qr Groupe Seb`).
- **Detección de site_prefix:** asume URLs tipo `/view/<site-id>/...`. Si Google Sites cambia el esquema (dominio custom, etc.), `__init__` necesita ajustes.

## UI generada — componente acordeón compartido

Tres lugares usan el mismo componente `.acc-item / .acc-header / .acc-body`:

1. **Home (`index.html`):** un acordeón por categoría. Al expandir muestra grid de items + link "Ver categoría completa".
2. **Categoría (`<cat>/index.html`):** un acordeón por item. Al expandir muestra preview de las primeras 3 secciones con contenido + "Ver ficha completa".
3. **Página individual (`<cat>/<item>.html`):** un acordeón por cada `<h2>` extraído (Tipo de Equipo, Función, Marca/Modelo, Especificaciones). Solo título visible por defecto.

Todos los acordeones empiezan **cerrados**. Se expanden individualmente. JS en `script.js` maneja toggle vía clase `.open` en `.acc-item`.

## Diseño mobile-first

- **Topbar fijo en móvil** con hamburger + título de página
- **Sidebar como overlay** con `transform: translateX(-100%)` → `0`, backdrop oscuro al 45% opacidad
- **Touch targets ≥44px** en todos los botones e items de menú
- **Grid responsivo** en items: 3 cols (desktop), 2 cols (mobile), 1 col (≤380px)
- **`<400px`:** oculta `.acc-meta` (texto secundario) para evitar truncado
- **Sidebar cierra automáticamente** al hacer click en un link en móvil (`matchMedia('(max-width: 900px)')`)
- **Escape cierra el sidebar**, scroll del body se bloquea cuando está abierto
- **Auto-scroll al ítem activo** del menú al cargar la página

## Convenciones del proyecto

- **Idioma:** todo en español — logs, docstrings, commits, documentación.
- **Logs con emojis** (🚀 🔍 📁 📄 ✅ ❌ 🏗️). Mantener el estilo.
- **Output por defecto:** `migrated_site/`. Sobrescribir con `--output`.
- **Site title:** autodetectado del header del Google Site. Override con `--site-title "Texto"`.
- **Historial:** `.migration_history` (formato `fecha | url | output`), escrito por [quick_migrate.sh](quick_migrate.sh) — pero `quick_migrate.sh` no expone el flag `--site-title`.
- **Entorno:** WSL2 Ubuntu 24 + VSCode Remote-WSL. Autor: Jorge Alberto — PROYECTOS CON INGENIERIA S.A.S. (Medellín).

## Archivos del repo

| Archivo | Estado |
|---|---|
| [google_sites_migrator.py](google_sites_migrator.py) | ✅ Script principal — actualizado con Playwright + acordeones |
| [requirements.txt](requirements.txt) | ⚠️ Desactualizado — falta `playwright`, sobra `requests` |
| [setup.sh](setup.sh) | ⚠️ Desactualizado — no instala Playwright ni Chromium |
| [quick_migrate.sh](quick_migrate.sh) | ⚠️ No expone `--site-title` |
| [examples/ejemplo_uso.py](examples/ejemplo_uso.py) | ⚠️ Puede romper en sitios sin las categorías hardcoded del original (ahora resueltas) |
| [README.md](README.md) | ⚠️ Documenta la versión vieja (regex, hardcoded) — necesita refresh |
| [QUICKSTART.md](QUICKSTART.md), [GUIA_USO.md](GUIA_USO.md), [VSCODE_README.md](VSCODE_README.md), [INDICE.md](INDICE.md) | ⚠️ Todos documentan la versión vieja |
| [.vscode/](.vscode/) | ✅ launch.json y tasks.json siguen siendo válidos |

[INDICE.md](INDICE.md) menciona un `ABRIR_DESDE_WINDOWS.md` que no existe.

## Mejoras pendientes

- Actualizar `setup.sh` para instalar Playwright + Chromium + libs nativas
- Actualizar `requirements.txt`: agregar `playwright`, quitar `requests`
- Refrescar los `.md` de documentación (todos describen la versión vieja con regex)
- Limpiar la carpeta espuria que se generaba en v1 (ya resuelto en v2)
- Considerar: filtrar items por prefijo numérico en la categoría index (agrupar 100-x, 200-x, etc.)
- Considerar: paralelizar el scraping de páginas (actualmente secuencial, ~3s por página)
- Considerar: cache de HTML descargado para re-runs durante desarrollo

## Limitaciones conocidas

- **Imágenes embebidas no se descargan.** Las URLs en `<img src>` (de `lh3.googleusercontent.com`) siguen apuntando a Google. Si Google las mueve, se rompen.
- **Tablas y elementos complejos no se preservan en el HTML generado.** El extractor solo toma texto plano por sección. Si una sección tiene una tabla en el Google Site, el HTML generado la muestra como texto corrido.
- **Sitios con autenticación o dominio Workspace** (`/u/0/d/`) no son accesibles desde Playwright sin login.
- **Setup requiere sudo una vez** para las libs nativas de Chromium — no es 100% sin permisos elevados.
