#!/bin/bash
# Quick Launcher para Google Sites Migrator
# Uso: ./quick_migrate.sh

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Google Sites → GitHub Pages Migrator                  ║"
echo "║   Quick Launcher v1.0                                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Verificar dependencias
check_dependencies() {
    print_info "Verificando dependencias..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 no está instalado"
        exit 1
    fi
    
    if ! python3 -c "import requests" 2>/dev/null; then
        print_warning "Instalando dependencias..."
        pip3 install -r requirements.txt
    fi
    
    print_success "Dependencias OK"
    echo ""
}

# Menú principal
show_menu() {
    echo "═══════════════════════════════════════════════════════════"
    echo "  Opciones:"
    echo "═══════════════════════════════════════════════════════════"
    echo "  1) Migrar sitio (ingresar URL manualmente)"
    echo "  2) Migrar sitio (URL desde portapapeles)"
    echo "  3) Migrar QR Groupe SEB (ejemplo pre-configurado)"
    echo "  4) Ver historial de migraciones"
    echo "  5) Ver ayuda"
    echo "  6) Salir"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    read -p "Selecciona una opción [1-6]: " choice
    echo ""
    
    case $choice in
        1) migrate_manual ;;
        2) migrate_clipboard ;;
        3) migrate_example ;;
        4) show_history ;;
        5) show_help ;;
        6) exit 0 ;;
        *) 
            print_error "Opción inválida"
            show_menu
            ;;
    esac
}

# Migrar con URL manual
migrate_manual() {
    print_info "Ingresa la URL del Google Site:"
    read -p "URL: " url
    
    if [[ ! "$url" =~ "sites.google.com" ]]; then
        print_error "La URL debe ser de un sitio de Google Sites"
        echo ""
        show_menu
        return
    fi
    
    print_info "Nombre del directorio de salida (Enter para auto-generar):"
    read -p "Output: " output
    
    if [ -z "$output" ]; then
        output="migrated_$(date +%Y%m%d_%H%M%S)"
    fi
    
    execute_migration "$url" "$output"
}

# Migrar desde portapapeles
migrate_clipboard() {
    if command -v pbpaste &> /dev/null; then
        # macOS
        url=$(pbpaste)
    elif command -v xclip &> /dev/null; then
        # Linux
        url=$(xclip -selection clipboard -o)
    else
        print_error "No se puede acceder al portapapeles"
        show_menu
        return
    fi
    
    print_info "URL detectada en portapapeles:"
    echo "  $url"
    echo ""
    
    read -p "¿Proceder con esta URL? [Y/n]: " confirm
    
    if [[ "$confirm" =~ ^[Nn]$ ]]; then
        show_menu
        return
    fi
    
    output="migrated_$(date +%Y%m%d_%H%M%S)"
    execute_migration "$url" "$output"
}

# Migrar ejemplo pre-configurado
migrate_example() {
    url="https://sites.google.com/view/qr-groupe-seb/EQUIPOS"
    output="qr_groupe_seb_$(date +%Y%m%d_%H%M%S)"
    
    print_info "Migrando sitio de ejemplo: QR Groupe SEB"
    execute_migration "$url" "$output"
}

# Ejecutar migración
execute_migration() {
    local url=$1
    local output=$2
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    print_info "Iniciando migración..."
    echo "  📍 URL: $url"
    echo "  📁 Output: $output"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    # Ejecutar script
    python3 google_sites_migrator.py "$url" --output "$output"
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "¡Migración completada exitosamente!"
        
        # Guardar en historial
        echo "$(date '+%Y-%m-%d %H:%M:%S') | $url | $output" >> .migration_history
        
        # Preguntar si abrir carpeta
        echo ""
        read -p "¿Abrir carpeta de salida? [Y/n]: " open_folder
        
        if [[ ! "$open_folder" =~ ^[Nn]$ ]]; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                open "$output"
            elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
                xdg-open "$output" 2>/dev/null || nautilus "$output" 2>/dev/null || echo "Abre manualmente: $output"
            fi
        fi
        
        # Preguntar si hacer deploy
        echo ""
        read -p "¿Quieres instrucciones para deploy en GitHub Pages? [Y/n]: " show_deploy
        
        if [[ ! "$show_deploy" =~ ^[Nn]$ ]]; then
            show_deploy_instructions "$output"
        fi
        
    else
        print_error "Error durante la migración"
    fi
    
    echo ""
    read -p "Presiona Enter para volver al menú..."
    show_menu
}

# Mostrar historial
show_history() {
    echo "═══════════════════════════════════════════════════════════"
    echo "  Historial de Migraciones"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    
    if [ -f .migration_history ]; then
        cat .migration_history | tail -10
    else
        print_info "No hay migraciones previas"
    fi
    
    echo ""
    read -p "Presiona Enter para volver al menú..."
    show_menu
}

# Mostrar ayuda
show_help() {
    echo "═══════════════════════════════════════════════════════════"
    echo "  Ayuda - Google Sites Migrator"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "Este script te ayuda a migrar sitios de Google Sites a"
    echo "GitHub Pages de forma automatizada."
    echo ""
    echo "Proceso:"
    echo "  1. Extrae contenido del Google Site"
    echo "  2. Genera sitio estático HTML/CSS/JS"
    echo "  3. Preserva enlaces a Google Drive"
    echo "  4. Crea estructura lista para GitHub Pages"
    echo ""
    echo "Requisitos:"
    echo "  - Python 3.7+"
    echo "  - pip (para instalar dependencias)"
    echo "  - Conexión a Internet"
    echo ""
    echo "Uso desde línea de comandos:"
    echo "  python3 google_sites_migrator.py <URL> [--output DIR]"
    echo ""
    echo "Para más información, consulta GUIA_USO.md"
    echo ""
    read -p "Presiona Enter para volver al menú..."
    show_menu
}

# Mostrar instrucciones de deploy
show_deploy_instructions() {
    local output_dir=$1
    
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo "  📦 Instrucciones para Deploy en GitHub Pages"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "1. Navega al directorio:"
    echo "   cd $output_dir"
    echo ""
    echo "2. Inicializa Git:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m \"Initial commit\""
    echo ""
    echo "3. Crea repo en GitHub (vía web o CLI):"
    echo "   gh repo create mi-sitio --public"
    echo ""
    echo "4. Push a GitHub:"
    echo "   git remote add origin https://github.com/TU_USUARIO/mi-sitio.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    echo ""
    echo "5. Activa GitHub Pages:"
    echo "   - Ve a Settings > Pages en GitHub"
    echo "   - Source: Deploy from a branch"
    echo "   - Branch: main, folder: / (root)"
    echo "   - Save"
    echo ""
    echo "Tu sitio estará en:"
    echo "   https://TU_USUARIO.github.io/mi-sitio/"
    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

# Main
main() {
    check_dependencies
    show_menu
}

# Ejecutar
main
