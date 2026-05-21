# 🚀 Google Sites Migrator - VSCode Project

> **Proyecto configurado para desarrollo y ejecución desde VSCode en WSL**

---

## 📁 Estructura del Proyecto

```
google-sites-migrator-project/
├── .vscode/                    # Configuración de VSCode
│   ├── launch.json            # Configuraciones de debug
│   ├── settings.json          # Settings del proyecto
│   └── tasks.json             # Tareas automatizadas
│
├── examples/                   # Ejemplos de uso
│   └── ejemplo_uso.py         # Ejemplos programáticos
│
├── tests/                      # Tests (futuro)
│
├── docs/                       # Documentación adicional
│
├── google_sites_migrator.py   # ⭐ Script principal
├── quick_migrate.sh           # Launcher interactivo
├── requirements.txt           # Dependencias Python
├── README.md                  # Documentación principal
├── GUIA_USO.md               # Guía completa de uso
├── VSCODE_README.md          # 👈 Este archivo
└── .gitignore                # Archivos a ignorar en Git
```

---

## ⚡ Quick Start desde VSCode

### 1️⃣ Abrir el Proyecto

```bash
# Desde WSL terminal
cd /home/claude/google-sites-migrator-project
code .
```

### 2️⃣ Instalar Dependencias

**Opción A - Desde Terminal Integrado:**
```bash
pip3 install -r requirements.txt
```

**Opción B - Desde Command Palette:**
- `Ctrl+Shift+P` → `Tasks: Run Task` → `Instalar Dependencias`

### 3️⃣ Ejecutar

**Opción A - Con Debug (F5):**
1. Presiona `F5`
2. Selecciona: "Python: Migrar Google Site"
3. El script ejecutará con la URL de ejemplo

**Opción B - Desde Terminal:**
```bash
python3 google_sites_migrator.py <URL>
```

**Opción C - Con Interfaz Interactiva:**
```bash
./quick_migrate.sh
```

---

## 🎯 Configuraciones de Debug Disponibles

### 1. Python: Migrar Google Site
Ejecuta con URL de ejemplo pre-configurada (QR Groupe SEB).

**Usar:** `F5` → Seleccionar esta opción

### 2. Python: Migrar Google Site (Custom URL)
Te pide URL y directorio de salida.

**Usar:** `F5` → Seleccionar esta opción → Ingresar datos

### 3. Python: Debug Current File
Debug del archivo Python que estés viendo.

**Usar:** Abrir archivo Python → `F5`

---

## 🛠️ Tareas Automatizadas (Tasks)

Acceder: `Ctrl+Shift+P` → `Tasks: Run Task`

| Tarea | Descripción | Atajo |
|-------|-------------|-------|
| **Instalar Dependencias** | Instala requirements.txt | - |
| **Ejecutar Quick Migrate** | Abre interfaz interactiva | - |
| **Migrar QR Groupe SEB** | Ejecuta migración de ejemplo | `Ctrl+Shift+B` |
| **Limpiar Outputs** | Borra carpetas de output | - |
| **Ver Historial** | Muestra migraciones previas | - |

**Build por defecto:** `Ctrl+Shift+B` ejecuta la migración de ejemplo.

---

## 🔧 Extensiones Recomendadas de VSCode

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-vscode-remote.remote-wsl",
    "yzhang.markdown-all-in-one",
    "streetsidesoftware.code-spell-checker"
  ]
}
```

Instalar: `Ctrl+Shift+P` → `Extensions: Show Recommended Extensions`

---

## 📝 Flujo de Trabajo Típico

### Migración Simple

1. Abrir terminal integrado: `` Ctrl+` ``
2. Ejecutar:
   ```bash
   python3 google_sites_migrator.py <URL>
   ```
3. Revisar output en carpeta generada
4. Hacer deploy (ver sección Deploy)

### Migración con Debug

1. Presionar `F5`
2. Seleccionar "Custom URL"
3. Ingresar URL cuando se solicite
4. Ver progreso en terminal integrado
5. Breakpoints funcionan si los agregas en el código

### Desarrollo/Modificación

1. Abrir `google_sites_migrator.py`
2. Agregar breakpoints (click izquierdo en número de línea)
3. Presionar `F5`
4. Step through con `F10` (over) o `F11` (into)
5. Ver variables en panel lateral

---

## 🖥️ Terminal Integrado

### Abrir Terminal
- `` Ctrl+` `` (backtick)
- O: `Ctrl+Shift+P` → `Terminal: Create New Terminal`

### Comandos Útiles

```bash
# Ver ayuda del script
python3 google_sites_migrator.py --help

# Migrar con output personalizado
python3 google_sites_migrator.py <URL> --output mi_sitio

# Ejecutar ejemplo programático
python3 examples/ejemplo_uso.py basico

# Ver historial
cat .migration_history

# Limpiar outputs
rm -rf migrated_site* output_*
```

---

## 🌐 Deploy a GitHub Pages desde VSCode

### Opción 1: Terminal Integrado

```bash
# 1. Navegar al output
cd migrated_site

# 2. Git init
git init
git add .
git commit -m "Sitio migrado desde Google Sites"

# 3. Crear repo (si tienes gh CLI)
gh repo create mi-sitio-migrado --public

# 4. Push
git remote add origin https://github.com/TU_USUARIO/mi-sitio-migrado.git
git branch -M main
git push -u origin main
```

### Opción 2: Source Control de VSCode

1. Abrir carpeta `migrated_site` en VSCode
2. Click en Source Control (ícono de Git)
3. Initialize Repository
4. Stage all changes (+)
5. Commit (✓)
6. Publish to GitHub

Luego activar Pages en la web de GitHub.

---

## 🐛 Debug Tips

### Ver Variables
- Hover sobre variable mientras debuggeas
- Panel "Variables" en sidebar izquierdo
- Watch expressions: click derecho → "Add to Watch"

### Breakpoints Condicionales
- Click derecho en breakpoint
- "Edit Breakpoint" → "Expression"
- Ejemplo: `len(self.pages_data) > 10`

### Debug Console
- Evaluar expresiones mientras debuggeas
- Acceso: `` Ctrl+Shift+` ``
- Ejemplo: `self.navigation.keys()`

---

## 🎨 Personalización de VSCode

### Cambiar Theme
`Ctrl+K Ctrl+T` → Seleccionar theme

Recomendados:
- Dark+ (default)
- Monokai
- Dracula Official

### Configurar Python Interpreter
`Ctrl+Shift+P` → `Python: Select Interpreter`

Seleccionar: `/usr/bin/python3` (WSL)

### Cambiar Font Size
Settings → `editor.fontSize`

---

## 📚 Recursos Adicionales

- [README.md](./README.md) - Documentación principal
- [GUIA_USO.md](./GUIA_USO.md) - Guía completa de uso
- [examples/](./examples/) - Ejemplos de código

---

## ⌨️ Shortcuts Útiles de VSCode

| Acción | Shortcut |
|--------|----------|
| Command Palette | `Ctrl+Shift+P` |
| Quick Open | `Ctrl+P` |
| Terminal | `` Ctrl+` `` |
| Run Task | `Ctrl+Shift+B` |
| Debug | `F5` |
| Step Over | `F10` |
| Step Into | `F11` |
| Continue | `F5` |
| Stop | `Shift+F5` |
| Find | `Ctrl+F` |
| Replace | `Ctrl+H` |
| Search All Files | `Ctrl+Shift+F` |
| Format Document | `Shift+Alt+F` |
| Go to Line | `Ctrl+G` |

---

## 🚨 Troubleshooting

### Error: "Python not found"
```bash
# Verificar instalación
which python3
python3 --version

# Si no está instalado
sudo apt update
sudo apt install python3 python3-pip
```

### Error: "Module not found"
```bash
pip3 install -r requirements.txt
```

### VSCode no reconoce imports
`Ctrl+Shift+P` → `Python: Select Interpreter` → Seleccionar `/usr/bin/python3`

### Terminal no es WSL
Settings → `terminal.integrated.defaultProfile.linux` → `bash`

---

## 💡 Tips Pro

1. **Multi-cursor editing**: `Alt+Click` o `Ctrl+Alt+Up/Down`
2. **Duplicate line**: `Shift+Alt+Down`
3. **Move line**: `Alt+Up/Down`
4. **Comment toggle**: `Ctrl+/`
5. **Zen mode**: `Ctrl+K Z` (distraction-free)
6. **Split editor**: `Ctrl+\`
7. **Close tab**: `Ctrl+W`
8. **Reopen closed tab**: `Ctrl+Shift+T`

---

## 📞 Soporte

- Consulta [README.md](./README.md) para documentación completa
- Revisa [GUIA_USO.md](./GUIA_USO.md) para casos de uso avanzados
- Ejecuta ejemplos en [examples/](./examples/)

---

**Desarrollado por:** Jorge Alberto - PROYECTOS CON INGENIERIA S.A.S.  
**Versión:** 1.0.0 - VSCode Edition  
**Última actualización:** Mayo 2026
