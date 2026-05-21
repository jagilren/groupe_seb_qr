# 🚀 Guía de Uso: Google Sites to GitHub Pages Migrator

## Opción 1: Ejecución por Demanda (Recomendada)

### Setup Inicial (una sola vez)

```bash
# 1. Clonar/copiar archivos a tu carpeta de trabajo
cd ~/Documents/herramientas-migracion
cp google_sites_migrator.py .
cp requirements.txt .

# 2. Instalar dependencias
pip install -r requirements.txt
```

### Uso

```bash
# Sintaxis básica
python google_sites_migrator.py <URL_GOOGLE_SITE>

# Ejemplo real
python google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb/EQUIPOS

# Con directorio personalizado
python google_sites_migrator.py https://sites.google.com/view/mi-sitio --output mi_sitio_nuevo
```

### Output

El script genera una carpeta con:
```
migrated_site/
├── index.html
├── styles.css
├── script.js
├── README.md
├── .gitignore
├── migration_metadata.json
├── equipos/
│   ├── index.html
│   ├── 800-P-01.html
│   └── ...
├── instrumentos/
│   └── ...
└── tanques/
    └── ...
```

---

## Opción 2: Integración con Cowork (Avanzada)

### Paso 1: Crear script wrapper

Crea `migrate_wrapper.sh`:

```bash
#!/bin/bash
# Wrapper para ejecutar el migrador desde Cowork

URL="$1"
OUTPUT="$2"

if [ -z "$URL" ]; then
    echo "❌ Error: Debes proporcionar una URL"
    echo "Uso: ./migrate_wrapper.sh <URL> [output_dir]"
    exit 1
fi

if [ -z "$OUTPUT" ]; then
    OUTPUT="migrated_site_$(date +%Y%m%d_%H%M%S)"
fi

echo "🚀 Iniciando migración..."
echo "📍 URL: $URL"
echo "📁 Output: $OUTPUT"
echo ""

python3 ~/Documents/herramientas-migracion/google_sites_migrator.py "$URL" --output "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migración exitosa"
    echo "📂 Abriendo carpeta..."
    open "$OUTPUT"  # macOS
    # xdg-open "$OUTPUT"  # Linux
fi
```

Hacer ejecutable:
```bash
chmod +x migrate_wrapper.sh
```

### Paso 2: Crear alias para ejecución rápida

Agrega a tu `~/.zshrc` o `~/.bashrc`:

```bash
# Migrador de Google Sites
alias migrate-site='~/Documents/herramientas-migracion/migrate_wrapper.sh'
```

Recargar:
```bash
source ~/.zshrc  # o source ~/.bashrc
```

### Uso con alias

```bash
# Ahora puedes ejecutar desde cualquier lugar
migrate-site https://sites.google.com/view/qr-groupe-seb/EQUIPOS

# O con output personalizado
migrate-site https://sites.google.com/view/mi-sitio proyecto_migrado
```

---

## Opción 3: Launcher Interactivo (GUI Simple)

### Usar el launcher HTML

1. Abrir `migration_launcher.html` en el navegador
2. Pegar la URL del Google Site
3. Click en "Iniciar Migración"
4. El script se ejecutará en segundo plano
5. Se abrirá la carpeta con los resultados

**Nota:** Requiere configurar un servidor local simple:
```bash
python -m http.server 8000
```

Abrir: `http://localhost:8000/migration_launcher.html`

---

## Opción 4: Automatización con n8n (Para workflows complejos)

Si usas n8n, puedes crear un workflow que:

1. Reciba URL vía webhook
2. Execute el script Python
3. Suba resultado a GitHub automáticamente
4. Envíe notificación a Slack/Email

Ejemplo de nodo Execute Command:
```json
{
  "command": "python3 ~/herramientas-migracion/google_sites_migrator.py {{ $json.url }}",
  "workingDirectory": "~/herramientas-migracion"
}
```

---

## Troubleshooting

### Error: "No module named 'requests'"
```bash
pip install -r requirements.txt
```

### Error: "Permission denied"
```bash
chmod +x google_sites_migrator.py
```

### Error: "No se pudo acceder al sitio base"
- Verifica que la URL sea correcta
- Verifica que el sitio sea público
- Prueba abrir la URL en el navegador

### Las páginas no tienen contenido
- Algunos sitios de Google Sites cargan contenido dinámicamente
- Revisa el archivo `migration_metadata.json` para ver qué se extrajo
- Considera usar la opción de Chrome/Cowork para sitios complejos

---

## Deploy a GitHub Pages

Una vez generado el sitio:

```bash
cd migrated_site

# Inicializar Git
git init
git add .
git commit -m "Initial commit: sitio migrado desde Google Sites"

# Crear repo en GitHub (vía web o gh CLI)
gh repo create mi-sitio-migrado --public

# Push
git remote add origin https://github.com/TU_USUARIO/mi-sitio-migrado.git
git branch -M main
git push -u origin main
```

Activar GitHub Pages:
1. Ir a Settings > Pages
2. Source: Deploy from a branch
3. Branch: main, folder: / (root)
4. Save

Tu sitio estará en: `https://TU_USUARIO.github.io/mi-sitio-migrado/`

---

## Integración con Cowork/Claude Desktop

Si quieres ejecutar esto desde Claude Desktop como una "herramienta":

1. **Vía MCP Server:** Crea un MCP server custom que ejecute el script
2. **Vía System Prompt:** Agrega path del script a tu context
3. **Vía Terminal Tool:** Ejecuta directamente con `bash_tool`

Ejemplo con Claude Desktop:
```
"Ejecuta el migrador en esta URL: https://sites.google.com/view/qr-groupe-seb/EQUIPOS"
```

Claude ejecutará:
```python
bash_tool(f"python3 ~/herramientas-migracion/google_sites_migrator.py {url}")
```

---

## Casos de Uso

### Caso 1: Migración One-Time
```bash
python google_sites_migrator.py <URL>
# Revisar output
# Deploy a GitHub Pages
# Listo ✅
```

### Caso 2: Múltiples Sitios (Batch)
```bash
# Crear lista de sitios
cat > sitios.txt <<EOF
https://sites.google.com/view/sitio1/home
https://sites.google.com/view/sitio2/home
https://sites.google.com/view/sitio3/home
EOF

# Migrar todos
while read url; do
    python google_sites_migrator.py "$url"
done < sitios.txt
```

### Caso 3: CI/CD Automatizado
```yaml
# .github/workflows/update-site.yml
name: Update Site
on:
  schedule:
    - cron: '0 0 * * 0'  # Cada domingo
  workflow_dispatch:

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run migration
        run: python google_sites_migrator.py ${{ secrets.SOURCE_URL }}
      - name: Deploy
        run: |
          git add .
          git commit -m "Auto-update from Google Site"
          git push
```

---

## Personalización

### Cambiar estilos
Edita `styles.css` en el output generado.

### Cambiar estructura de navegación
Edita `generate_navigation_html()` en el script.

### Agregar funcionalidades
El script es modular, puedes agregar:
- Descarga de imágenes
- Conversión de Google Docs embebidos
- Generación de sitemap.xml
- Optimización de SEO

---

## Soporte

Para problemas o mejoras:
1. Revisa `migration_metadata.json` para debug
2. Ejecuta con `python -v` para modo verbose
3. Contacta al equipo TI

**Mantenido por:** Jorge Alberto - PROYECTOS CON INGENIERIA S.A.S.
**Versión:** 1.0.0
**Última actualización:** 2026-05-21
