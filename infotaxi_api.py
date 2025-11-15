"""
API REST para Sistema InfoTaxi con Swagger UI
Servicios de gestión de usuarios y reportes
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flasgger import Swagger, swag_from
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import io
from functools import wraps

app = Flask(__name__)

# Configurar CORS de manera más permisiva
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-User-Celular", "Authorization"]
    },
    r"/apidocs/*": {
        "origins": "*",
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/apispec.json": {
        "origins": "*",
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ==================== CONFIGURACIÓN SWAGGER ====================
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API InfoTaxi",
        "description": "Sistema de gestión de reportes de conductores de taxi",
        "version": "1.0.0",
        "contact": {
            "name": "Soporte API",
            "email": "jandrezapata@hotmail.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "CelularAuth": {
            "type": "apiKey",
            "name": "X-User-Celular",
            "in": "header",
            "description": "Número de celular del usuario autenticado"
        }
    },
    "consumes": ["application/json"],
    "produces": ["application/json"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Manejar preflight requests (OPTIONS)
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,X-User-Celular,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

# Manejar preflight requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-User-Celular,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Manejar errores globales (solo para excepciones no capturadas)
@app.errorhandler(500)
def handle_500_error(e):
    """Manejar errores 500"""
    print(f"[ERROR 500] Error del servidor: {str(e)}")
    import traceback
    traceback.print_exc()
    response = jsonify({
        'success': False,
        'message': f'Error del servidor: {str(e)}'
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-User-Celular,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response, 500

@app.errorhandler(400)
def handle_bad_request(e):
    """Manejar errores de solicitud incorrecta"""
    return jsonify({
        'success': False,
        'message': 'Solicitud incorrecta: ' + str(e)
    }), 400

# ==================== CONFIGURACIÓN BASE DE DATOS ====================
DB_CONFIG = {
    'host': '31.97.130.20',
    'port': 4646,
    'database': 'electo',
    'user': 'mariadb',
    'password': '9204a8246f7ed4fe49e6'
}

def get_db_connection():
    """Crear conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

# ==================== DECORADOR DE AUTENTICACIÓN ====================
def verificar_usuario(f):
    """Decorador para verificar que el usuario existe por número de celular"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        celular = request.headers.get('X-User-Celular')
        
        if not celular:
            return jsonify({
                'success': False,
                'message': 'Número de celular requerido en headers (X-User-Celular)'
            }), 401
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a BD'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_user, username, nombres, rol FROM users WHERE Celular = %s AND isactive = 1",
                (celular,)
            )
            usuario = cursor.fetchone()
            
            if not usuario:
                return jsonify({
                    'success': False,
                    'message': 'Usuario no encontrado o inactivo'
                }), 403
            
            request.usuario = usuario
            
        except Error as e:
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
        
        return f(*args, **kwargs)
    
    return decorated_function

# ==================== SERVICIO 1: VERIFICAR USUARIO ====================
@app.route('/api/verificar-usuario', methods=['POST'])
def verificar_usuario_existe():
    """
    Verificar si un usuario existe por número de celular
    ---
    tags:
      - Usuarios
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - celular
          properties:
            celular:
              type: string
              example: "3007471199"
              description: Número de celular del usuario
    responses:
      200:
        description: Usuario encontrado o no encontrado
        schema:
          type: object
          properties:
            success:
              type: boolean
            exists:
              type: boolean
            usuario:
              type: object
              properties:
                id:
                  type: integer
                nombre:
                  type: string
                email:
                  type: string
                rol:
                  type: string
                activo:
                  type: boolean
      400:
        description: Parámetros incorrectos
      500:
        description: Error del servidor
    """
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al procesar JSON: ' + str(e)
        }), 400
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'No se recibió ningún dato JSON'
        }), 400
    
    celular = data.get('celular')
    
    if not celular:
        return jsonify({
            'success': False,
            'message': 'Número de celular requerido'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_user, username, nombres, Celular, rol, isactive 
            FROM users 
            WHERE Celular = %s
        """, (celular,))
        
        usuario = cursor.fetchone()
        
        if usuario:
            return jsonify({
                'success': True,
                'exists': True,
                'usuario': {
                    'id': usuario['id_user'],
                    'nombre': usuario['nombres'],
                    'email': usuario['username'],
                    'rol': usuario['rol'],
                    'activo': bool(usuario['isactive'])
                }
            }), 200
        else:
            return jsonify({
                'success': True,
                'exists': False,
                'message': 'Usuario no encontrado'
            }), 200
            
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== SERVICIO 2: CREAR USUARIO ====================
@app.route('/api/usuarios', methods=['POST', 'OPTIONS'])
def crear_usuario():
    """
    Crear nuevo usuario con rol 'usuario'
    ---
    tags:
      - Usuarios
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - nombres
            - celular
            - password
          properties:
            username:
              type: string
              example: "usuario@ejemplo.com"
              description: Email del usuario
            nombres:
              type: string
              example: "Juan Pérez"
              description: Nombre completo
            celular:
              type: string
              example: "3001234567"
              description: Número de celular
            password:
              type: string
              example: "contraseña123"
              description: Contraseña del usuario
    responses:
      201:
        description: Usuario creado exitosamente
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            id_user:
              type: integer
      400:
        description: Parámetros incorrectos
      409:
        description: Usuario ya existe
      500:
        description: Error del servidor
    """
    try:
        print(f"[DEBUG] POST /api/usuarios - Método: {request.method}")
        print(f"[DEBUG] Headers: {dict(request.headers)}")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        
        if request.method == 'OPTIONS':
            response = jsonify({'status': 'ok'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,X-User-Celular,Authorization")
            response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
            return response
        
        try:
            print(f"[DEBUG] Intentando obtener JSON...")
            data = request.get_json(force=True)
            print(f"[DEBUG] JSON recibido: {data}")
        except Exception as e:
            print(f"[ERROR] Error al procesar JSON: {str(e)}")
            import traceback
            traceback.print_exc()
            response = jsonify({
                'success': False,
                'message': 'Error al procesar JSON: ' + str(e)
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        if not data:
            print("[ERROR] No se recibió ningún dato JSON")
            response = jsonify({
                'success': False,
                'message': 'No se recibió ningún dato JSON'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        print(f"[DEBUG] Validando campos requeridos...")
        required = ['username', 'nombres', 'celular', 'password']
        if not all(field in data for field in required):
            missing = [field for field in required if field not in data]
            print(f"[ERROR] Campos faltantes: {missing}")
            response = jsonify({
                'success': False,
                'message': f'Campos requeridos faltantes: {", ".join(missing)}'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 400
        
        print(f"[DEBUG] Conectando a la base de datos...")
        conn = get_db_connection()
        if not conn:
            print("[ERROR] No se pudo conectar a la base de datos")
            response = jsonify({'success': False, 'message': 'Error de conexión a la base de datos'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        
        print(f"[DEBUG] Conexión a BD exitosa")
        
        try:
            print(f"[DEBUG] Creando cursor...")
            cursor = conn.cursor()
            
            # Verificar si el usuario ya existe
            print(f"[DEBUG] Verificando si el usuario ya existe...")
            cursor.execute("SELECT id_user FROM users WHERE Celular = %s OR username = %s",
                          (data['celular'], data['username']))
            existing = cursor.fetchone()
            if existing:
                print(f"[WARN] Usuario ya existe: {existing}")
                response = jsonify({
                    'success': False,
                    'message': 'Ya existe un usuario con ese celular o email'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 409
            
            # Validar que los campos no estén vacíos
            if not data['username'] or not data['nombres'] or not data['celular'] or not data['password']:
                print(f"[ERROR] Campos vacíos detectados")
                response = jsonify({
                    'success': False,
                    'message': 'Todos los campos son requeridos y no pueden estar vacíos'
                })
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 400
            
            # Hash de la contraseña
            print(f"[DEBUG] Generando hash de contraseña...")
            password_hash = hashlib.sha1(data['password'].encode()).hexdigest()
            
            # Insertar nuevo usuario
            print(f"[DEBUG] Insertando nuevo usuario...")
            query = """
                INSERT INTO users (username, nombres, Celular, rol, password, isactive)
                VALUES (%s, %s, %s, 'usuario', %s, 1)
            """
            cursor.execute(query, (
                data['username'],
                data['nombres'],
                data['celular'],
                password_hash
            ))
            conn.commit()
            
            user_id = cursor.lastrowid
            print(f"[SUCCESS] Usuario creado exitosamente con ID: {user_id}")
            
            response = jsonify({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'id_user': user_id
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 201
            
        except Error as e:
            print(f"[ERROR] Error de base de datos: {str(e)}")
            import traceback
            traceback.print_exc()
            if conn and conn.is_connected():
                conn.rollback()
            response = jsonify({
                'success': False,
                'message': f'Error de base de datos: {str(e)}'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        except Exception as e:
            print(f"[ERROR] Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            if conn and conn.is_connected():
                conn.rollback()
            response = jsonify({
                'success': False,
                'message': f'Error inesperado: {str(e)}'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                print(f"[DEBUG] Conexión cerrada")
                
    except Exception as e:
        # Capturar cualquier error no manejado
        print(f"[ERROR CRÍTICO] Error no capturado en crear_usuario: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            'success': False,
            'message': f'Error crítico: {str(e)}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-User-Celular,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response, 500

# ==================== SERVICIO 3: CONSULTAR PERSONA POR CÉDULA ====================
@app.route('/api/personas/<cedula>', methods=['GET'])
@verificar_usuario
def consultar_persona(cedula):
    """
    Consultar persona reportada por número de cédula
    ---
    tags:
      - Reportes
    security:
      - CelularAuth: []
    parameters:
      - name: cedula
        in: path
        type: string
        required: true
        description: Número de documento de identidad
        example: "8497643"
      - name: X-User-Celular
        in: header
        type: string
        required: true
        description: Número de celular del usuario autenticado
        example: "3007471199"
    responses:
      200:
        description: Resultados de la búsqueda
        schema:
          type: object
          properties:
            success:
              type: boolean
            found:
              type: boolean
            total_reportes:
              type: integer
            total_consultas:
              type: integer
              description: Total de consultas realizadas por el usuario
            reportes:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  fecha_reporte:
                    type: string
                  numero_documento:
                    type: string
                  nombres:
                    type: string
                  apellidos:
                    type: string
                  placa:
                    type: string
                  valor_reporte:
                    type: integer
                  descripcion:
                    type: string
                  estado:
                    type: string
      401:
        description: No autorizado
      403:
        description: Usuario inactivo
      500:
        description: Error del servidor
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Buscar persona
        cursor.execute("""
            SELECT id, Fecha_Reporte, Numero_Documento, Nombres, Apellidos,
                   Fecha_cierre, Placa, Valor_Reporte, Descripcion_Reporte,
                   Vehiculo_afiliado, Estado, Reportante_Nombres
            FROM personas
            WHERE Numero_Documento = %s
            ORDER BY Fecha_Reporte DESC
        """, (cedula,))
        
        reportes = cursor.fetchall()
        
        if not reportes:
            return jsonify({
                'success': True,
                'found': False,
                'message': 'No se encontraron reportes para esta cédula',
                'total_consultas': 0
            }), 200
        
        # Registrar consulta (sumar +1 al contador)
        cursor.execute("""
            SELECT id, count FROM consultas 
            WHERE user_id = %s
            ORDER BY id DESC LIMIT 1
        """, (request.usuario['id_user'],))
        
        consulta_existente = cursor.fetchone()
        
        if consulta_existente:
            nuevo_count = consulta_existente['count'] + 1
            cursor.execute("""
                UPDATE consultas 
                SET count = %s 
                WHERE id = %s
            """, (nuevo_count, consulta_existente['id']))
            total_consultas = nuevo_count
        else:
            cursor.execute("""
                INSERT INTO consultas (user_id, count)
                VALUES (%s, 1)
            """, (request.usuario['id_user'],))
            total_consultas = 1
        
        conn.commit()
        
        # Formatear respuesta
        reportes_formateados = []
        for r in reportes:
            reportes_formateados.append({
                'id': r['id'],
                'fecha_reporte': r['Fecha_Reporte'].strftime('%Y-%m-%d') if r['Fecha_Reporte'] else None,
                'numero_documento': r['Numero_Documento'],
                'nombres': r['Nombres'],
                'apellidos': r['Apellidos'],
                'fecha_cierre': r['Fecha_cierre'],
                'placa': r['Placa'],
                'valor_reporte': r['Valor_Reporte'],
                'descripcion': r['Descripcion_Reporte'],
                'vehiculo_afiliado': r['Vehiculo_afiliado'],
                'estado': r['Estado']
            })
        
        return jsonify({
            'success': True,
            'found': True,
            'total_reportes': len(reportes),
            'total_consultas': total_consultas,
            'reportes': reportes_formateados
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== SERVICIO 4: DESCARGAR PLANTILLA EXCEL ====================
@app.route('/api/plantilla-excel', methods=['GET'])
@verificar_usuario
def descargar_plantilla():
    """
    Descargar plantilla Excel para importación masiva
    ---
    tags:
      - Reportes
    security:
      - CelularAuth: []
    parameters:
      - name: X-User-Celular
        in: header
        type: string
        required: true
        description: Número de celular del usuario autenticado
        example: "3007471199"
    responses:
      200:
        description: Archivo Excel
        content:
          application/vnd.openxmlformats-officedocument.spreadsheetml.sheet:
            schema:
              type: string
              format: binary
      401:
        description: No autorizado
      500:
        description: Error del servidor
    """
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "Plantilla Reportes"
        
        headers = [
            'Fecha_Reporte', 'Numero_Documento', 'Nombres', 'Apellidos',
            'Fecha_cierre', 'Placa', 'Valor_Reporte', 'Descripcion_Reporte',
            'Vehiculo_afiliado', 'Estado'
        ]
        
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        ejemplo = [
            '2024-01-15', '1234567890', 'JUAN', 'PEREZ GOMEZ',
            '', 'ABC123', '50000', 'REPORTE NEGATIVO POR TARIFAS',
            'ADMICARS', 'ACTIVA'
        ]
        
        for col, valor in enumerate(ejemplo, 1):
            ws.cell(row=2, column=col, value=valor)
        
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column].width = max_length + 2
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'plantilla_reportes_{datetime.now().strftime("%Y%m%d")}.xlsx'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==================== SERVICIO 5: IMPORTAR DATOS MASIVOS DESDE EXCEL ====================
@app.route('/api/importar-excel', methods=['POST'])
@verificar_usuario
def importar_excel():
    """
    Importar datos masivos desde archivo Excel
    ---
    tags:
      - Reportes
    security:
      - CelularAuth: []
    consumes:
      - multipart/form-data
    parameters:
      - name: X-User-Celular
        in: header
        type: string
        required: true
        description: Número de celular del usuario autenticado
        example: "3007471199"
      - name: file
        in: formData
        type: file
        required: true
        description: Archivo Excel (.xlsx o .xls) con los datos a importar
    responses:
      200:
        description: Importación completada
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            insertados:
              type: integer
            errores:
              type: integer
            detalle_errores:
              type: array
              items:
                type: string
      400:
        description: Archivo no válido
      401:
        description: No autorizado
      500:
        description: Error del servidor
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No se proporcionó archivo'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'Archivo vacío'
        }), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({
            'success': False,
            'message': 'Formato no válido. Use .xlsx o .xls'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        df = pd.read_excel(file)
        
        required_cols = ['Numero_Documento', 'Nombres', 'Apellidos', 'Placa']
        if not all(col in df.columns for col in required_cols):
            return jsonify({
                'success': False,
                'message': f'Columnas requeridas: {", ".join(required_cols)}'
            }), 400
        
        cursor = conn.cursor()
        insertados = 0
        errores = []
        
        for idx, row in df.iterrows():
            try:
                query = """
                    INSERT INTO personas (
                        Fecha_Reporte, Numero_Documento, Nombres, Apellidos,
                        Fecha_cierre, Placa, Valor_Reporte, Descripcion_Reporte,
                        Vehiculo_afiliado, Estado, Reportante_Nombres
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                valores = (
                    row.get('Fecha_Reporte', datetime.now().date()),
                    row['Numero_Documento'],
                    row['Nombres'],
                    row['Apellidos'],
                    row.get('Fecha_cierre', ''),
                    row['Placa'],
                    row.get('Valor_Reporte', 0),
                    row.get('Descripcion_Reporte', ''),
                    row.get('Vehiculo_afiliado', 'ADMICARS'),
                    row.get('Estado', 'ACTIVA'),
                    request.usuario['id_user']
                )
                
                cursor.execute(query, valores)
                insertados += 1
                
            except Exception as e:
                errores.append(f"Fila {idx + 2}: {str(e)}")
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Importación completada',
            'insertados': insertados,
            'errores': len(errores),
            'detalle_errores': errores[:10]
        }), 200
        
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== SERVICIO 6: CREAR REPORTE INDIVIDUAL ====================
@app.route('/api/personas', methods=['POST'])
@verificar_usuario
def crear_persona():
    """
    Crear un reporte individual
    ---
    tags:
      - Reportes
    security:
      - CelularAuth: []
    parameters:
      - name: X-User-Celular
        in: header
        type: string
        required: true
        description: Número de celular del usuario autenticado
        example: "3007471199"
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - numero_documento
            - nombres
            - apellidos
            - placa
          properties:
            numero_documento:
              type: string
              example: "1234567890"
            nombres:
              type: string
              example: "JUAN"
            apellidos:
              type: string
              example: "PEREZ GOMEZ"
            placa:
              type: string
              example: "ABC123"
            valor_reporte:
              type: integer
              example: 50000
            descripcion:
              type: string
              example: "REPORTE NEGATIVO POR TARIFAS"
            vehiculo_afiliado:
              type: string
              example: "ADMICARS"
            estado:
              type: string
              example: "ACTIVA"
    responses:
      201:
        description: Reporte creado exitosamente
      400:
        description: Parámetros incorrectos
      401:
        description: No autorizado
      500:
        description: Error del servidor
    """
    try:
        data = request.get_json(force=True)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al procesar JSON: ' + str(e)
        }), 400
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'No se recibió ningún dato JSON'
        }), 400
    
    required = ['numero_documento', 'nombres', 'apellidos', 'placa']
    if not all(field in data for field in required):
        return jsonify({
            'success': False,
            'message': 'Campos requeridos: numero_documento, nombres, apellidos, placa'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO personas (
                Fecha_Reporte, Numero_Documento, Nombres, Apellidos,
                Placa, Valor_Reporte, Descripcion_Reporte,
                Vehiculo_afiliado, Estado, Reportante_Nombres
            ) VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            data['numero_documento'],
            data['nombres'].upper(),
            data['apellidos'].upper(),
            data['placa'].upper(),
            data.get('valor_reporte', 0),
            data.get('descripcion', ''),
            data.get('vehiculo_afiliado', 'ADMICARS'),
            data.get('estado', 'ACTIVA'),
            request.usuario['id_user']
        ))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reporte creado exitosamente',
            'id': cursor.lastrowid
        }), 201
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== SERVICIO 7: EDITAR REPORTE ====================
@app.route('/api/personas/<int:id>', methods=['PUT'])
@verificar_usuario
def editar_persona(id):
    """
    Editar un reporte (solo si lo creó el usuario o es admin)
    ---
    tags:
      - Reportes
    security:
      - CelularAuth: []
    parameters:
      - name: X-User-Celular
        in: header
        type: string
        required: true
        description: Número de celular del usuario autenticado
        example: "3007471199"
      - name: id
        in: path
        type: integer
        required: true
        description: ID del reporte a editar
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombres:
              type: string
            apellidos:
              type: string
            placa:
              type: string
            valor_reporte:
              type: integer
            descripcion_reporte:
              type: string
            estado:
              type: string
            fecha_cierre:
              type: string
    responses:
      200:
        description: Reporte actualizado exitosamente
      400:
        description: No hay campos para actualizar
      401:
        description: No autorizado
      403:
        description: Sin permisos para editar
      404:
        description: Reporte no encontrado
      500:
        description: Error del servidor
    """
    try:
        data = request.get_json(force=True) or {}
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error al procesar JSON: ' + str(e)
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT Reportante_Nombres FROM personas WHERE id = %s
        """, (id,))
        
        reporte = cursor.fetchone()
        
        if not reporte:
            return jsonify({
                'success': False,
                'message': 'Reporte no encontrado'
            }), 404
        
        es_admin = request.usuario['rol'] == 'admin'
        es_creador = str(reporte['Reportante_Nombres']) == str(request.usuario['id_user'])
        
        if not (es_admin or es_creador):
            return jsonify({
                'success': False,
                'message': 'No tiene permisos para editar este reporte'
            }), 403
        
        campos_permitidos = [
            'Nombres', 'Apellidos', 'Placa', 'Valor_Reporte',
            'Descripcion_Reporte', 'Estado', 'Fecha_cierre'
        ]
        
        campos_actualizar = []
        valores = []
        
        for campo in campos_permitidos:
            campo_lower = campo.lower().replace('_', '')
            for key in data.keys():
                if key.lower().replace('_', '') == campo_lower:
                    campos_actualizar.append(f"{campo} = %s")
                    valores.append(data[key])
                    break
        
        if not campos_actualizar:
            return jsonify({
                'success': False,
                'message': 'No hay campos para actualizar'
            }), 400
        
        valores.append(id)
        query = f"UPDATE personas SET {', '.join(campos_actualizar)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reporte actualizado exitosamente'
        }), 200
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== SERVICIO EXTRA: ESTADÍSTICAS DE USUARIO ====================
@app.route('/api/estadisticas', methods=['GET'])
@verificar_usuario
def obtener_estadisticas():
    """
    Obtener estadísticas del usuario actual
    ---
    tags:
      - Estadísticas
    security:
      - CelularAuth: []
    parameters:
      - name: X-User-Celular
        in: header
        type: string
        required: true
        description: Número de celular del usuario autenticado
        example: "3007471199"
    responses:
      200:
        description: Estadísticas del usuario
        schema:
          type: object
          properties:
            success:
              type: boolean
            usuario:
              type: object
            total_consultas:
              type: integer
            reportes_creados:
              type: integer
      401:
        description: No autorizado
      500:
        description: Error del servidor
    """
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Total de consultas
        cursor.execute("""
            SELECT COALESCE(SUM(count), 0) as total
            FROM consultas
            WHERE user_id = %s
        """, (request.usuario['id_user'],))
        total_consultas = cursor.fetchone()['total']
        
        # Reportes creados por el usuario
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM personas
            WHERE Reportante_Nombres = %s
        """, (request.usuario['id_user'],))
        reportes_creados = cursor.fetchone()['total']
        
        return jsonify({
            'success': True,
            'usuario': {
                'id': request.usuario['id_user'],
                'nombre': request.usuario['nombres'],
                'email': request.usuario['username'],
                'rol': request.usuario['rol']
            },
            'total_consultas': total_consultas,
            'reportes_creados': reportes_creados
        }), 200
        
    except Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== RUTA DE PRUEBA ====================
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """
    Verificar que la API está funcionando
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API funcionando correctamente
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            timestamp:
              type: string
            database:
              type: string
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,X-User-Celular,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response
    
    try:
        conn = get_db_connection()
        db_status = "Conectada" if conn else "Error de conexión"
        if conn and conn.is_connected():
            conn.close()
        
        response = jsonify({
            'success': True,
            'message': 'API InfoTaxi funcionando correctamente',
            'timestamp': datetime.now().isoformat(),
            'database': db_status,
            'swagger_docs': '/apidocs/'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        response = jsonify({
            'success': False,
            'message': f'Error en health check: {str(e)}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# ==================== RUTA PRINCIPAL ====================
@app.route('/', methods=['GET'])
def index():
    """
    Página de inicio - Redirige a documentación Swagger
    ---
    tags:
      - Sistema
    responses:
      200:
        description: Información de la API
    """
    return jsonify({
        'message': 'API InfoTaxi',
        'version': '1.0.0',
        'documentacion': '/apidocs/',
        'endpoints': {
            'health': '/api/health',
            'verificar_usuario': '/api/verificar-usuario',
            'crear_usuario': '/api/usuarios',
            'consultar_persona': '/api/personas/<cedula>',
            'plantilla_excel': '/api/plantilla-excel',
            'importar_excel': '/api/importar-excel',
            'crear_reporte': '/api/personas',
            'editar_reporte': '/api/personas/<id>',
            'estadisticas': '/api/estadisticas'
        }
    }), 200

# ==================== INICIAR SERVIDOR ====================
if __name__ == '__main__':
    print("=" * 60)
    print("🚕 API InfoTaxi iniciando...")
    print("=" * 60)
    print(f"📡 Servidor: http://localhost:5000")
    print(f"📚 Documentación Swagger: http://localhost:5000/apidocs/")
    print(f"🔍 Health Check: http://localhost:5000/api/health")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)