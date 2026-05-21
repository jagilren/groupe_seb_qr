#!/bin/bash
# Setup automático del proyecto Google Sites Migrator
# Ejecutar una sola vez después de clonar el proyecto

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Google Sites Migrator - Setup Automático              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Verificar Python
print_step "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "Instalando Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi
PYTHON_VERSION=$(python3 --version)
print_success "Python instalado: $PYTHON_VERSION"
echo ""

# 2. Verificar pip
print_step "Verificando pip..."
if ! command -v pip3 &> /dev/null; then
    echo "Instalando pip..."
    sudo apt install -y python3-pip
fi
PIP_VERSION=$(pip3 --version)
print_success "pip instalado: $PIP_VERSION"
echo ""

# 3. Instalar dependencias
print_step "Instalando dependencias del proyecto..."
pip3 install -r requirements.txt
print_success "Dependencias instaladas"
echo ""

# 4. Hacer scripts ejecutables
print_step "Configurando permisos de ejecución..."
chmod +x google_sites_migrator.py
chmod +x quick_migrate.sh
chmod +x examples/ejemplo_uso.py
print_success "Permisos configurados"
echo ""

# 5. Crear directorios necesarios
print_step "Creando directorios de trabajo..."
mkdir -p tests
mkdir -p docs
mkdir -p .cache
print_success "Directorios creados"
echo ""

# 6. Verificar Git
print_step "Verificando Git..."
if ! command -v git &> /dev/null; then
    print_warning "Git no está instalado (opcional)"
    echo "Para instalar: sudo apt install git"
else
    GIT_VERSION=$(git --version)
    print_success "Git instalado: $GIT_VERSION"
fi
echo ""

# 7. Inicializar Git (opcional)
if [ ! -d .git ]; then
    read -p "¿Inicializar repositorio Git? [Y/n]: " init_git
    if [[ ! "$init_git" =~ ^[Nn]$ ]]; then
        print_step "Inicializando Git..."
        git init
        git add .
        git commit -m "Initial commit: Google Sites Migrator project setup"
        print_success "Git inicializado"
    fi
fi
echo ""

# 8. Test de funcionamiento
print_step "Ejecutando test básico..."
python3 -c "from google_sites_migrator import GoogleSitesMigrator; print('✅ Import exitoso')"
print_success "Test básico completado"
echo ""

# 9. Resumen
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   ✅ Setup Completado                                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📂 Proyecto listo en: $(pwd)"
echo ""
echo "🚀 Próximos pasos:"
echo ""
echo "1. Abrir en VSCode:"
echo "   code ."
echo ""
echo "2. Ejecutar migración de ejemplo:"
echo "   python3 google_sites_migrator.py https://sites.google.com/view/qr-groupe-seb/EQUIPOS"
echo ""
echo "3. O usar interfaz interactiva:"
echo "   ./quick_migrate.sh"
echo ""
echo "4. Leer documentación:"
echo "   - README.md (documentación principal)"
echo "   - VSCODE_README.md (guía de VSCode)"
echo "   - GUIA_USO.md (guía completa de uso)"
echo ""
echo "📚 Para más información:"
echo "   cat VSCODE_README.md"
echo ""
