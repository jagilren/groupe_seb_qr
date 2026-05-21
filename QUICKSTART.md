# ⚡ QUICK START - Uso Inmediato desde VSCode

> **El proyecto ya está listo en tu WSL. Sigue estos pasos.**

---

## 🎯 Setup Inicial (Solo una vez)

### Paso 1: Abrir VSCode desde WSL

```bash
# En tu terminal WSL:
cd /home/claude/google-sites-migrator-project
code .
```

**Espera 5-10 segundos** mientras VSCode:
- Conecta con WSL
- Carga el proyecto
- Instala extensiones recomendadas (te preguntará)

### Paso 2: Ejecutar Setup Automático

**Opción A - Desde Terminal Integrado en VSCode:**

1. Abre terminal: `` Ctrl+` ``
2. Ejecuta:
   ```bash
   ./setup.sh
   ```
3. Presiona `Y` cuando pregunte sobre Git (recomendado)

**Opción B - Manual:**

```bash
pip3 install -r requirements.txt
chmod +x *.sh *.py
```

---

## 🚀 Primera Ejecución (Migrar QR Groupe SEB)

### Método 1: Con Debug (F5) - RECOMENDADO

1. **Presiona `F5`**
2. Selecciona: `Python: Migrar Google Site`
3. **¡Listo!** El script ejecuta automáticamente

Ver progreso en el terminal integrado:
```
🔍 Iniciando escaneo del sitio...
📁 Categorías encontradas: ['EQUIPOS', 'INSTRUMENTOS', 'TANQUES']
📄 Total de páginas a procesar: 58
[1/58] Procesando: https://...
...
✅ MIGRACIÓN COMPLETADA
```

### Método 2: Desde Terminal

```bash
# Terminal integrado (Ctrl+`)
python3 google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb/EQUIPOS
```

### Método 3: Con Interfaz Gráfica

```bash
./quick_migrate.sh
```

Aparece menú → Selecciona opción 3 (Ejemplo QR Groupe SEB)

---

## 📂 Revisar Resultados

### Desde VSCode Explorer

1. Mira el panel izquierdo (Explorer)
2. Verás carpeta `migrated_site/` (o el nombre que elegiste)
3. Click derecho → "Reveal in File Explorer"

### Desde Terminal

```bash
cd migrated_site
ls -la
```

### Ver el Sitio Localmente

```bash
cd migrated_site
python3 -m http.server 8000
```

Abrir navegador: `http://localhost:8000`

---

## 🎮 Controles de VSCode que Usarás

| Acción | Atajo | Para Qué |
|--------|-------|----------|
| **Ejecutar** | `F5` | Migrar sitio con debug |
| **Build** | `Ctrl+Shift+B` | Migrar ejemplo rápido |
| **Terminal** | `` Ctrl+` `` | Abrir/cerrar terminal |
| **Tasks** | `Ctrl+Shift+P` → Tasks | Ver tareas disponibles |
| **Command Palette** | `Ctrl+Shift+P` | Acceso a comandos |

---

## 🔄 Flujo de Trabajo Típico

```
1. Abrir VSCode (code .)
   ↓
2. Presionar F5
   ↓
3. Seleccionar config de debug
   ↓
4. Ver ejecución en terminal
   ↓
5. Revisar output en Explorer
   ↓
6. Deploy a GitHub (ver abajo)
```

---

## 🌐 Deploy a GitHub Pages

Una vez que tienes `migrated_site/`:

```bash
cd migrated_site

# Init Git
git init
git add .
git commit -m "Sitio migrado desde Google Sites"

# Crear repo en GitHub (CLI)
gh repo create mi-sitio-qr --public

# O crear repo en web y luego:
git remote add origin https://github.com/TU_USUARIO/mi-sitio-qr.git

# Push
git branch -M main
git push -u origin main
```

**Activar GitHub Pages:**
1. Ir a repo en GitHub
2. Settings → Pages
3. Source: Deploy from a branch
4. Branch: `main`, folder: `/root`
5. Save

Tu sitio estará en: `https://TU_USUARIO.github.io/mi-sitio-qr/`

---

## 🎓 Migrar OTRO Sitio

### Opción 1: Custom URL en Debug

1. Presiona `F5`
2. Selecciona: `Python: Migrar Google Site (Custom URL)`
3. Ingresa tu URL cuando pida
4. Ingresa nombre de output

### Opción 2: Desde Terminal

```bash
python3 google_sites_migrator.py <TU_URL>

# Ejemplo:
python3 google_sites_migrator.py https://sites.google.com/view/mi-planta/equipos --output mi_planta
```

### Opción 3: Interfaz Interactiva

```bash
./quick_migrate.sh
```
Selecciona opción 1 o 2 del menú.

---

## 🐛 Si Algo Falla

### Error: "Python not found"
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Error: "Module not found: requests"
```bash
pip3 install -r requirements.txt
```

### VSCode no conecta con WSL
- Asegúrate que WSL está corriendo
- Reinstala extensión Remote - WSL
- Cierra y reabre VSCode

### El script no se ejecuta
```bash
chmod +x google_sites_migrator.py quick_migrate.sh
```

---

## 📚 Siguientes Pasos

1. **Leer documentación completa:**
   - `VSCODE_README.md` - Guía de VSCode
   - `README.md` - Documentación principal
   - `GUIA_USO.md` - Casos de uso avanzados

2. **Ver ejemplos de código:**
   ```bash
   python3 examples/ejemplo_uso.py basico
   ```

3. **Personalizar el script:**
   - Edita `google_sites_migrator.py`
   - Agrega breakpoints
   - Debug con `F5`

---

## 💡 Tips Pro

- **Múltiples terminales:** `` Ctrl+Shift+` ``
- **Split terminal:** Click en ícono de split
- **Cambiar entre archivos:** `Ctrl+P` → nombre del archivo
- **Buscar en todo el proyecto:** `Ctrl+Shift+F`
- **Format código:** `Shift+Alt+F`

---

## ✅ Checklist de Verificación

- [ ] VSCode abierto en el proyecto
- [ ] `./setup.sh` ejecutado exitosamente
- [ ] `F5` funciona y muestra opciones de debug
- [ ] Primera migración ejecutada correctamente
- [ ] Carpeta `migrated_site/` generada
- [ ] Sitio visible en `localhost:8000`

---

## 🎯 Resumen en 4 Comandos

```bash
# 1. Abrir proyecto
code /home/claude/google-sites-migrator-project

# 2. Setup (en terminal de VSCode)
./setup.sh

# 3. Migrar
python3 google_sites_migrator.py <URL>

# 4. Ver resultado
cd migrated_site && python3 -m http.server 8000
```

---

**¿Listo?** Presiona `F5` y comienza tu primera migración. 🚀

**¿Dudas?** Consulta `VSCODE_README.md` para detalles completos.
