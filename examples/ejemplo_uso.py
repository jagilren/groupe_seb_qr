#!/usr/bin/env python3
"""
Ejemplo de uso del Google Sites Migrator
Este script muestra cómo usar el migrador programáticamente
"""

from google_sites_migrator import GoogleSitesMigrator
import sys

def ejemplo_basico():
    """Ejemplo básico de migración"""
    print("=" * 60)
    print("EJEMPLO 1: Migración Básica")
    print("=" * 60)
    
    url = "https://sites.google.com/view/qr-groupe-seb/EQUIPOS"
    output = "ejemplo_output"
    
    migrator = GoogleSitesMigrator(url, output)
    migrator.run()
    
    print(f"\n✅ Ejemplo completado. Revisa la carpeta: {output}/")


def ejemplo_personalizado():
    """Ejemplo con personalización"""
    print("=" * 60)
    print("EJEMPLO 2: Migración con Personalización")
    print("=" * 60)
    
    url = "https://sites.google.com/view/qr-groupe-seb/EQUIPOS"
    output = "ejemplo_personalizado"
    
    # Crear instancia del migrador
    migrator = GoogleSitesMigrator(url, output)
    
    # Ejecutar solo scraping
    migrator.scrape_site()
    
    # Ver estadísticas
    print(f"\n📊 Estadísticas:")
    print(f"   - Páginas encontradas: {len(migrator.pages_data)}")
    print(f"   - Categorías: {len(migrator.navigation)}")
    
    for category, urls in migrator.navigation.items():
        print(f"   - {category}: {len(urls)} páginas")
    
    # Continuar con generación
    migrator.generate_static_site()
    migrator.generate_github_files()
    migrator.save_metadata()
    
    print(f"\n✅ Ejemplo completado. Revisa la carpeta: {output}/")


def ejemplo_batch():
    """Ejemplo de migración batch de múltiples sitios"""
    print("=" * 60)
    print("EJEMPLO 3: Migración Batch")
    print("=" * 60)
    
    sitios = [
        "https://sites.google.com/view/qr-groupe-seb/EQUIPOS",
        # Agrega más URLs aquí
    ]
    
    for i, url in enumerate(sitios, 1):
        print(f"\n[{i}/{len(sitios)}] Migrando: {url}")
        output = f"batch_output_{i}"
        
        migrator = GoogleSitesMigrator(url, output)
        migrator.run()
    
    print("\n✅ Migración batch completada")


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        ejemplo = sys.argv[1]
        
        if ejemplo == "basico":
            ejemplo_basico()
        elif ejemplo == "personalizado":
            ejemplo_personalizado()
        elif ejemplo == "batch":
            ejemplo_batch()
        else:
            print("Uso: python ejemplo_uso.py [basico|personalizado|batch]")
    else:
        print("\n🎯 Ejemplos disponibles:\n")
        print("1. python ejemplo_uso.py basico")
        print("   → Migración básica simple")
        print()
        print("2. python ejemplo_uso.py personalizado")
        print("   → Migración con estadísticas y control")
        print()
        print("3. python ejemplo_uso.py batch")
        print("   → Migración de múltiples sitios")
        print()
        print("Selecciona un ejemplo para ejecutar.")


if __name__ == "__main__":
    main()
