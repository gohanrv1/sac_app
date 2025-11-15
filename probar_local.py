"""
Script para probar que Swagger funcione correctamente en local
"""
import requests
import time
import sys

BASE_URL = "http://localhost:5000"

def test_swagger_local():
    """Probar Swagger en local"""
    print("=" * 60)
    print("🧪 PRUEBA LOCAL DE SWAGGER")
    print("=" * 60)
    
    print("\n⚠️  Asegúrate de que el servidor esté corriendo:")
    print("   python infotaxi_api.py")
    print("\nEsperando 3 segundos...")
    time.sleep(3)
    
    # Test 1: Health check
    print("\n1. Probando /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Health check OK (Status: {response.status_code})")
            print(f"   📄 Respuesta: {response.json()}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: No se puede conectar al servidor")
        print("   💡 Inicia el servidor con: python infotaxi_api.py")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False
    
    # Test 2: Swagger UI
    print("\n2. Probando Swagger UI (/apidocs/)...")
    try:
        response = requests.get(f"{BASE_URL}/apidocs/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Swagger UI accesible (Status: {response.status_code})")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test 3: apispec.json
    print("\n3. Probando /apispec.json...")
    try:
        response = requests.get(f"{BASE_URL}/apispec.json", timeout=5)
        if response.status_code == 200:
            spec = response.json()
            print(f"   ✅ Especificación accesible (Status: {response.status_code})")
            print(f"   📋 Host en spec: {spec.get('host', 'No especificado')}")
            print(f"   📋 Schemes: {spec.get('schemes', [])}")
            
            # Verificar que el host sea correcto
            if spec.get('host') == 'localhost:5000':
                print("   ✅ Host correcto: localhost:5000")
            else:
                print(f"   ⚠️  Host inesperado: {spec.get('host')}")
        else:
            print(f"   ❌ Error: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return False
    
    # Test 4: CORS headers
    print("\n4. Verificando headers CORS...")
    try:
        response = requests.options(f"{BASE_URL}/api/health", timeout=5)
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        if cors_origin == '*' or cors_origin:
            print(f"   ✅ CORS configurado: {cors_origin}")
        else:
            print("   ⚠️  CORS no configurado")
    except Exception as e:
        print(f"   ⚠️  Error verificando CORS: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 60)
    print("\n📚 Ahora abre en tu navegador:")
    print(f"   {BASE_URL}/apidocs/")
    print("\n💡 Si ves 'Failed to fetch' en Swagger UI:")
    print("   1. Verifica que el servidor esté corriendo")
    print("   2. Abre la consola del navegador (F12) y revisa errores")
    print("   3. Prueba acceder directamente a: http://localhost:5000/api/health")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_swagger_local()
    sys.exit(0 if success else 1)

