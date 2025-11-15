"""
Script para probar los endpoints principales de la API
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def test_health():
    """Probar endpoint de health"""
    print_section("Probando /api/health")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_verificar_usuario():
    """Probar verificar usuario"""
    print_section("Probando POST /api/verificar-usuario")
    data = {"celular": "3006413771"}
    try:
        response = requests.post(
            f"{BASE_URL}/api/verificar-usuario",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_crear_usuario():
    """Probar crear usuario"""
    print_section("Probando POST /api/usuarios")
    timestamp = int(time.time())
    data = {
        "celular": "3006413771",
        "nombres": "Usuario Test",
        "password": "test123456",
        "username": f"test_{timestamp}@ejemplo.com"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        if response.status_code in [201, 409]:
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_swagger_ui():
    """Verificar que Swagger UI esté disponible"""
    print_section("Verificando Swagger UI")
    try:
        response = requests.get(f"{BASE_URL}/apidocs/", timeout=5)
        if response.status_code == 200:
            print(f"✅ Swagger UI accesible (Status: {response.status_code})")
            print(f"📚 URL: {BASE_URL}/apidocs/")
            return True
        else:
            print(f"⚠️  Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 PRUEBAS DE API InfoTaxi")
    print("="*60)
    print(f"URL Base: {BASE_URL}")
    print("\n⚠️  Asegúrate de que el servidor esté corriendo")
    print("   python infotaxi_api.py")
    print("\nEsperando 2 segundos...")
    time.sleep(2)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health()))
    
    # Test 2: Swagger UI
    results.append(("Swagger UI", test_swagger_ui()))
    
    # Test 3: Verificar Usuario
    results.append(("Verificar Usuario", test_verificar_usuario()))
    
    # Test 4: Crear Usuario
    results.append(("Crear Usuario", test_crear_usuario()))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print(f"\n📚 Abre Swagger UI en: {BASE_URL}/apidocs/")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("   Revisa los errores arriba")

