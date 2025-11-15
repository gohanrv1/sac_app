"""
Script para instalar y verificar todas las dependencias necesarias
"""
import subprocess
import sys

dependencias = [
    "Flask==3.0.2",
    "flask-cors==4.0.1",
    "mysql-connector-python==8.3.0",
    "Flasgger==0.9.7.1",
    "pandas==2.2.2",
    "openpyxl==3.1.2",
    "python-dotenv==1.0.1"
]

print("=" * 60)
print("📦 Instalando dependencias...")
print("=" * 60)

for dep in dependencias:
    print(f"\nInstalando {dep}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        print(f"✅ {dep} instalado correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando {dep}: {e}")
        sys.exit(1)

print("\n" + "=" * 60)
print("🔍 Verificando instalación...")
print("=" * 60)

# Verificar importaciones
modulos = [
    ("flask", "Flask"),
    ("flask_cors", "CORS"),
    ("flasgger", "Swagger"),
    ("mysql.connector", "mysql.connector"),
    ("pandas", "pandas"),
    ("openpyxl", "openpyxl"),
    ("dotenv", "python-dotenv")
]

errores = []
for modulo, nombre in modulos:
    try:
        __import__(modulo)
        print(f"✅ {nombre} importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando {nombre}: {e}")
        errores.append(nombre)

if errores:
    print(f"\n❌ Errores al importar: {', '.join(errores)}")
    sys.exit(1)
else:
    print("\n" + "=" * 60)
    print("✅ Todas las dependencias están instaladas correctamente!")
    print("=" * 60)
    print("\nAhora puedes iniciar el servidor con:")
    print("   python infotaxi_api.py")

