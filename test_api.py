"""
Script de prueba para verificar que la API funciona correctamente
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    """Probar endpoint de health"""
    print("\n" + "="*60)
    print("🔍 Probando /api/health")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor. ¿Está corriendo?")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_crear_usuario():
    """Probar crear usuario"""
    print("\n" + "="*60)
    print("👤 Probando POST /api/usuarios")
    print("="*60)
    
    # Datos de prueba
    usuario_data = {
        "celular": "3006413771",
        "nombres": "Juan Pérez Test",
        "password": "contraseña123",
        "username": f"test_{int(time.time())}@ejemplo.com"  # Email único
    }
    
    print(f"Datos a enviar: {json.dumps(usuario_data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/usuarios",
            json=usuario_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code in [201, 409]:  # 201 = creado, 409 = ya existe
            print("✅ Test exitoso")
            return True
        else:
            print("⚠️ Respuesta inesperada")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se puede conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_verificar_usuario():
    """Probar verificar usuario"""
    print("\n" + "="*60)
    print("🔎 Probando POST /api/verificar-usuario")
    print("="*60)
    
    data = {"celular": "3006413771"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/verificar-usuario",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 PRUEBAS DE API InfoTaxi")
    print("="*60)
    print(f"URL Base: {BASE_URL}")
    print("\n⚠️  Asegúrate de que el servidor esté corriendo:")
    print("   python infotaxi_api.py")
    print("\nEsperando 2 segundos antes de comenzar las pruebas...")
    time.sleep(2)
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health()))
    
    # Test 2: Verificar Usuario
    results.append(("Verificar Usuario", test_verificar_usuario()))
    
    # Test 3: Crear Usuario
    results.append(("Crear Usuario", test_crear_usuario()))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} pruebas pasadas")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        sys.exit(0)
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        sys.exit(1)

