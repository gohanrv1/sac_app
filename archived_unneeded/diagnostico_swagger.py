"""
Script de diagnóstico para verificar problemas con Swagger UI
"""
import requests
import sys

BASE_URL = "http://localhost:5000"

def test_server():
    """Verificar que el servidor esté corriendo"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE SWAGGER UI")
    print("=" * 60)
    
    # Test 1: Verificar que el servidor esté corriendo
    print("\n1. Verificando que el servidor esté corriendo...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Servidor respondiendo (Status: {response.status_code})")
            print(f"   📄 Respuesta: {response.json()}")
        else:
            print(f"   ⚠️  Servidor respondió con status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: No se puede conectar al servidor")
        print("   💡 Solución: Asegúrate de que el servidor esté corriendo:")
        print("      python infotaxi_api.py")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False
    
    # Test 2: Verificar Swagger UI
    print("\n2. Verificando Swagger UI...")
    try:
        response = requests.get(f"{BASE_URL}/apidocs/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Swagger UI accesible (Status: {response.status_code})")
        else:
            print(f"   ⚠️  Swagger UI respondió con status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR accediendo a Swagger UI: {str(e)}")
    
    # Test 3: Verificar apispec.json
    print("\n3. Verificando especificación de Swagger...")
    try:
        response = requests.get(f"{BASE_URL}/apispec.json", timeout=5)
        if response.status_code == 200:
            spec = response.json()
            print(f"   ✅ Especificación accesible (Status: {response.status_code})")
            print(f"   📋 Host en spec: {spec.get('host', 'No especificado')}")
            print(f"   📋 Schemes: {spec.get('schemes', [])}")
        else:
            print(f"   ⚠️  Especificación respondió con status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR accediendo a especificación: {str(e)}")
    
    # Test 4: Verificar CORS
    print("\n4. Verificando headers CORS...")
    try:
        response = requests.options(f"{BASE_URL}/api/health", timeout=5)
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        print(f"   📋 Headers CORS:")
        for key, value in cors_headers.items():
            if value:
                print(f"      ✅ {key}: {value}")
            else:
                print(f"      ⚠️  {key}: No presente")
    except Exception as e:
        print(f"   ❌ ERROR verificando CORS: {str(e)}")
    
    # Test 5: Probar endpoint directamente
    print("\n5. Probando endpoint /api/health directamente...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   ✅ Endpoint funciona correctamente")
        print(f"   📄 Respuesta: {response.json()}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📝 RECOMENDACIONES:")
    print("=" * 60)
    print("1. Si el servidor no está corriendo, inícialo con: python infotaxi_api.py")
    print("2. Abre Swagger UI en: http://localhost:5000/apidocs/")
    print("3. Si ves 'Failed to fetch', verifica:")
    print("   - Que el servidor esté corriendo")
    print("   - Que no haya errores en la consola del servidor")
    print("   - Que puedas acceder a http://localhost:5000/api/health directamente")
    print("4. Prueba en otro navegador o en modo incógnito")
    print("5. Revisa la consola del navegador (F12) para ver errores de JavaScript")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_server()

