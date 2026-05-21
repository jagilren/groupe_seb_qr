# CLAUDE.md

Guía para Claude Code cuando trabaje en este repositorio.

## Objetivo principal

Generar una **carpeta de sitio estático** lista para:
- **Opción A:** Subirla a un repo de GitHub y activar GitHub Pages.
- **Opción B:** Importarla/servirla en cualquier otro hosting (Netlify, Vercel, S3, servidor propio, o local con `python3 -m http.server`).

El input es la URL de un Google Site. El output es una carpeta autosuficiente (HTML + CSS + JS + metadata) que **no requiere build step**.

## Flujo end-to-end (lo que el usuario quiere ejecutar)

```bash
# 1. Setup (una sola vez)
./setup.sh                                    # instala deps + permisos
# (o manualmente: pip3 install -r requirements.txt)

# 2. Generar la carpeta del sitio
python3 google_sites_migrator.py <URL_GOOGLE_SITE> --output mi_sitio

# 3a. Ver el sitio localmente antes de subir
cd mi_sitio && python3 -m http.server 8000
# → abrir http://localhost:8000

# 3b. Deploy a GitHub Pages
cd mi_sitio
git init && git add . && git commit -m "Sitio migrado desde Google Sites"
gh repo create mi-sitio --public --source=. --remote=origin --push
# Luego en GitHub: Settings → Pages → Source: main / (root) → Save
# URL final: https://<usuario>.github.io/mi-sitio/

# 3c. Importar a otro hosting
# La carpeta es 100% estática — súbela tal cual a Netlify, Vercel, etc.
```

Ejemplo canónico de referencia (sitio de pruebas):
```bash
python3 google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb/EQUIPOS
```

## Estructura del output generado

```
mi_sitio/
├── index.html                  # Página principal
├── styles.css                  # Estilos globales (sidebar + responsive)
├── script.js                   # Toggle de submenús + highlight de página activa
├── README.md                   # Instrucciones de deploy (auto-generado)
├── .gitignore                  # Listo para commit
├── migration_metadata.json     # Trazabilidad: URL origen, fecha, páginas, links
└── <categoria>/                # Una carpeta por categoría detectada
    ├── index.html              # Índice de la categoría
    └── <item_id>.html          # Una página por item
```

Todo es estático puro — sin Node, sin build, sin servidor. Funciona en cualquier hosting de archivos.

## Comandos secundarios

```bash
# Menú interactivo (pide URL, ofrece historial, abre carpeta)
./quick_migrate.sh

# Ejemplos programáticos (uso como librería)
python3 examples/ejemplo_uso.py [basico|personalizado|batch]

# Limpiar outputs de prueba
rm -rf migrated_site* output_* example_output qr_groupe_seb_* .migration_history
```

En VSCode: `F5` lanza una de las configs de [.vscode/launch.json](.vscode/launch.json). `Ctrl+Shift+B` ejecuta la migración de ejemplo vía [.vscode/tasks.json](.vscode/tasks.json).

## Arquitectura del migrador

Un solo módulo: [google_sites_migrator.py](google_sites_migrator.py). Toda la lógica está en la clase `GoogleSitesMigrator`. Pipeline lineal expuesto vía `run()`:

1. `scrape_site()` — fetch del HTML base + recorrido de páginas vinculadas
2. `extract_navigation()` — parsea links siguiendo el patrón `/CATEGORIA/ITEM`
3. `extract_page_content()` — extrae título (h1), secciones (h2) y enlaces externos a Drive/Docs
4. `generate_static_site()` — escribe HTML por categoría usando `generate_html_template()`
5. `generate_github_files()` — README.md + .gitignore en el output
6. `save_metadata()` — `migration_metadata.json` con trazabilidad

Datos extraídos en memoria como `List[PageContent]` (dataclass en [google_sites_migrator.py:26-34](google_sites_migrator.py#L26-L34)).

### Decisiones de diseño con impacto práctico

- **Parsing con regex, no BeautifulSoup.** `requirements.txt` lista bs4 y lxml, pero el código solo usa `re`. Si el parsing falla en un sitio nuevo, considera reescribir con bs4 (ya está instalado).
- **Nombre del sitio hardcoded como "QR Groupe SEB"** en `generate_static_site()` ([google_sites_migrator.py:416,436,446](google_sites_migrator.py#L416)). Para otros sitios, edita esos strings o parametrízalo antes de migrar.
- **Categorías hardcoded en la regex de navegación.** [google_sites_migrator.py:68](google_sites_migrator.py#L68) solo reconoce `EQUIPOS|INSTRUMENTOS|TANQUES`. Sitios con otras categorías necesitan que ese patrón se generalice o parametrice — si no, la navegación saldrá vacía.
- **Contenido dinámico (JS-rendered) no se extrae.** Páginas que cargan vía JS aparecerán vacías. Revisar `migration_metadata.json` para detectar esto.
- **Enlaces a Drive se preservan tal cual** (no se descargan ni rehospedan). Verificar que sean públicos antes de migrar.

## Convenciones del proyecto

- **Idioma:** todo en español — mensajes de log, docstrings, commits, documentación. Mantener.
- **Logs con emojis** (🔍 📁 📄 ✅ ❌ 🏗️). Mantener el estilo.
- **Output por defecto:** `migrated_site/`. Sobrescribir con `--output`.
- **Historial:** [quick_migrate.sh](quick_migrate.sh) anexa a `.migration_history` con formato `fecha | url | output`.
- **Entorno:** WSL Ubuntu + VSCode Remote-WSL. Autor: Jorge Alberto — PROYECTOS CON INGENIERIA S.A.S. (Medellín). Versión 1.0.0 (mayo 2026).

## Mapa de documentación

| Archivo | Audiencia |
|---|---|
| [README.md](README.md) | Documentación canónica completa |
| [QUICKSTART.md](QUICKSTART.md) | Onboarding rápido (F5 en VSCode) |
| [GUIA_USO.md](GUIA_USO.md) | Casos avanzados (wrappers, n8n, CI/CD) |
| [VSCODE_README.md](VSCODE_README.md) | Flujo VSCode + debug + tasks |
| [INDICE.md](INDICE.md) | Índice y mapa de lectura |

[INDICE.md](INDICE.md) menciona un `ABRIR_DESDE_WINDOWS.md` que no existe — eliminar la referencia o crear el archivo.

## Extensiones pendientes (mencionadas en docs, no implementadas)

- Descarga de imágenes locales
- Generación de `sitemap.xml`
- Búsqueda con Fuse.js
- Google Analytics en el template
- MCP server custom que exponga el migrador como herramienta de Claude
