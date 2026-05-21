# 📚 Índice Completo del Proyecto

## 📂 Estructura del Proyecto

```
google-sites-migrator-project/
│
├── 📖 DOCUMENTACIÓN
│   ├── README.md                    ⭐ Documentación principal
│   ├── QUICKSTART.md                ⚡ Inicio rápido (EMPIEZA AQUÍ)
│   ├── VSCODE_README.md             🎨 Guía completa de VSCode
│   ├── GUIA_USO.md                  📘 Casos de uso avanzados
│   ├── ABRIR_DESDE_WINDOWS.md       🪟 Cómo abrir desde Windows
│   └── INDICE.md                    📚 Este archivo
│
├── 🚀 SCRIPTS PRINCIPALES
│   ├── google_sites_migrator.py     ⭐ Script principal de migración
│   ├── quick_migrate.sh             🎯 Launcher interactivo con menú
│   └── setup.sh                     ⚙️ Setup automático del proyecto
│
├── 📦 CONFIGURACIÓN
│   ├── requirements.txt             📋 Dependencias Python
│   └── .gitignore                   🚫 Archivos ignorados por Git
│
├── 🎓 EJEMPLOS Y TESTS
│   ├── examples/
│   │   └── ejemplo_uso.py           💡 Ejemplos programáticos
│   ├── tests/                       🧪 Tests (futuro)
│   └── docs/                        📄 Documentación adicional
│
└── ⚙️ CONFIGURACIÓN VSCODE
    └── .vscode/
        ├── launch.json              🐛 Configuraciones de debug
        ├── settings.json            ⚙️ Settings del workspace
        ├── tasks.json               📋 Tareas automatizadas
        └── extensions.json          🔌 Extensiones recomendadas
```

---

## 🎯 Orden de Lectura Recomendado

### Para Empezar Ahora (5 minutos)

1. **`ABRIR_DESDE_WINDOWS.md`** - Cómo abrir el proyecto
2. **`QUICKSTART.md`** - Primera ejecución
3. Presionar `F5` en VSCode

### Para Entender el Proyecto (15 minutos)

4. **`README.md`** - Visión general y características
5. **`VSCODE_README.md`** - Flujo de trabajo en VSCode
6. Ejecutar `./setup.sh`

### Para Dominar la Herramienta (30 minutos)

7. **`GUIA_USO.md`** - Casos de uso avanzados
8. **`examples/ejemplo_uso.py`** - Código de ejemplo
9. Personalizar el script según necesidad

---

## 🚀 Flujos de Trabajo

### 1️⃣ Primera Vez (Setup)

```
ABRIR_DESDE_WINDOWS.md → Abrir VSCode → ./setup.sh → F5
```

### 2️⃣ Uso Diario (Migrar Sitios)

```
code . → F5 → Ingresar URL → Revisar output → Deploy
```

### 3️⃣ Desarrollo/Personalización

```
Editar .py → Agregar breakpoints → F5 → Debug → Commit
```

---

## 📖 Descripción de Archivos

### 🌟 Archivos Esenciales

| Archivo | Para Qué | Cuándo Leer |
|---------|----------|-------------|
| **QUICKSTART.md** | Empezar rápido | Primera vez |
| **google_sites_migrator.py** | Script principal | Para ejecutar/modificar |
| **setup.sh** | Configurar proyecto | Una sola vez al inicio |

### 📚 Documentación

| Archivo | Contenido | Público Objetivo |
|---------|-----------|------------------|
| **README.md** | Overview completo | Todos |
| **VSCODE_README.md** | Guía de VSCode | Usuarios de VSCode |
| **GUIA_USO.md** | Casos avanzados | Usuarios experimentados |
| **ABRIR_DESDE_WINDOWS.md** | Acceso desde Windows | Usuarios de WSL |

### 🔧 Configuración

| Archivo | Propósito |
|---------|-----------|
| **requirements.txt** | Dependencias Python a instalar |
| **.vscode/launch.json** | Configs de debug (F5) |
| **.vscode/tasks.json** | Tareas (Ctrl+Shift+B) |
| **.vscode/settings.json** | Settings del proyecto |
| **.gitignore** | Archivos ignorados por Git |

### 💻 Scripts

| Script | Descripción | Uso |
|--------|-------------|-----|
| **google_sites_migrator.py** | Migrador principal | `python3 google_sites_migrator.py <URL>` |
| **quick_migrate.sh** | Interfaz interactiva | `./quick_migrate.sh` |
| **setup.sh** | Setup automatizado | `./setup.sh` |
| **ejemplo_uso.py** | Ejemplos de código | `python3 examples/ejemplo_uso.py basico` |

---

## 🎬 Primeros Pasos en 3 Comandos

```bash
# 1. Abrir (desde Windows)
wsl code /home/claude/google-sites-migrator-project

# 2. Setup (en terminal VSCode)
./setup.sh

# 3. Primera migración (presiona F5 en VSCode)
# O desde terminal:
python3 google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb/EQUIPOS
```

---

## ❓ FAQ Rápidas

**P: ¿Por dónde empiezo?**  
R: Lee `ABRIR_DESDE_WINDOWS.md`, luego `QUICKSTART.md`

**P: ¿Cómo ejecuto una migración?**  
R: Presiona `F5` en VSCode

**P: ¿Cómo personalizo el script?**  
R: Edita `google_sites_migrator.py` y debuggea con `F5`

**P: ¿Dónde están los outputs?**  
R: Carpetas `migrated_site/` o `output_*/` en el proyecto

**P: ¿Cómo hago deploy?**  
R: Consulta sección "Deploy a GitHub Pages" en `QUICKSTART.md`

---

## 🔗 Enlaces Rápidos a Secciones

- [Abrir desde Windows](./ABRIR_DESDE_WINDOWS.md)
- [Quick Start](./QUICKSTART.md)
- [Documentación Principal](./README.md)
- [Guía de VSCode](./VSCODE_README.md)
- [Casos de Uso Avanzados](./GUIA_USO.md)
- [Script Principal](./google_sites_migrator.py)
- [Ejemplos de Código](./examples/ejemplo_uso.py)

---

## 📞 Ayuda

1. **Problemas técnicos:** Consulta sección Troubleshooting en `VSCODE_README.md`
2. **Casos de uso:** Consulta `GUIA_USO.md`
3. **Dudas de código:** Revisa `examples/ejemplo_uso.py`

---

## ✅ Checklist de Verificación

- [ ] Proyecto abierto en VSCode desde WSL
- [ ] `./setup.sh` ejecutado exitosamente
- [ ] Extensiones recomendadas instaladas
- [ ] `F5` funciona (muestra opciones de debug)
- [ ] Primera migración ejecutada
- [ ] Output revisado en Explorer

---

## 🎓 Niveles de Uso

### 🟢 Nivel Básico
- Abrir proyecto
- Ejecutar con `F5`
- Revisar outputs
- Deploy manual

**Archivos:** QUICKSTART.md, VSCODE_README.md

### 🟡 Nivel Intermedio
- Personalizar URLs
- Usar quick_migrate.sh
- Deploy automatizado
- Múltiples sitios

**Archivos:** README.md, GUIA_USO.md

### 🔴 Nivel Avanzado
- Modificar script
- Debug con breakpoints
- Integración CI/CD
- MCP servers custom

**Archivos:** google_sites_migrator.py, ejemplo_uso.py

---

## 🎯 Resumen Ejecutivo

**Proyecto:** Herramienta para migrar Google Sites a GitHub Pages  
**Stack:** Python 3 + HTML/CSS/JS  
**Objetivo:** Automatizar migraciones en segundos  
**Output:** Sitio estático listo para deploy  

**Empezar:** `QUICKSTART.md` → `F5` → ¡Listo!

---

**Desarrollado por:** Jorge Alberto - PROYECTOS CON INGENIERIA S.A.S.  
**Versión:** 1.0.0  
**Última actualización:** Mayo 2026
