"""
API REST para Sistema InfoTaxi
Servicios de gestión de usuarios y reportes
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flasgger import Swagger
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import io
import os
from functools import wraps

app = Flask(__name__)
CORS(app)

# Configurar Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API InfoTaxi",
        "description": "API REST para Sistema InfoTaxi - Servicios de gestión de usuarios y reportes",
        "version": "1.0.0"
    },
    "basePath": "/",
    "schemes": ["http", "https"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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
            
            # Pasar información del usuario a la función
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
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - celular
          properties:
            celular:
              type: string
              example: "3007471199"
    responses:
      200:
        description: Respuesta exitosa
        schema:
          type: object
          properties:
            success:
              type: boolean
            exists:
              type: boolean
            usuario:
              type: object
            message:
              type: string
      400:
        description: Error de validación
      500:
        description: Error del servidor
    """
    data = request.get_json()
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
@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    """
    Crear nuevo usuario con rol 'usuario'
    ---
    tags:
      - Usuarios
    parameters:
      - in: body
        name: body
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
              example: "email@ejemplo.com"
            nombres:
              type: string
              example: "Nombre Completo"
            celular:
              type: string
              example: "3001234567"
            password:
              type: string
              example: "contraseña123"
    responses:
      201:
        description: Usuario creado exitosamente
      400:
        description: Error de validación
      409:
        description: Usuario ya existe
      500:
        description: Error del servidor
    """
    data = request.get_json()
    
    # Validar campos requeridos
    required = ['username', 'nombres', 'celular', 'password']
    if not all(field in data for field in required):
        return jsonify({
            'success': False,
            'message': 'Campos requeridos: username, nombres, celular, password'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT id_user FROM users WHERE Celular = %s OR username = %s",
                      (data['celular'], data['username']))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'Ya existe un usuario con ese celular o email'
            }), 409
        
        # Hash de contraseña (SHA1 para compatibilidad, pero recomiendo migrar a bcrypt)
        password_hash = hashlib.sha1(data['password'].encode()).hexdigest()
        
        # Insertar usuario
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
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'id_user': cursor.lastrowid
        }), 201
        
    except Error as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# ==================== SERVICIO 3: CONSULTAR PERSONA POR CÉDULA ====================
@app.route('/api/personas/<cedula>', methods=['GET'])
@verificar_usuario
def consultar_persona(cedula):
    """
    Consultar persona reportada por número de cédula
    Headers: X-User-Celular: 3007471199
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
                'message': 'No se encontraron reportes para esta cédula'
            }), 200
        
        # Registrar consulta (sumar +1 al contador)
        # Verificar si el usuario ya tiene registro de consultas
        cursor.execute("""
            SELECT id, count FROM consultas 
            WHERE user_id = %s
            ORDER BY id DESC LIMIT 1
        """, (request.usuario['id_user'],))
        
        consulta_existente = cursor.fetchone()
        
        if consulta_existente:
            # Si existe, actualizar sumando +1
            nuevo_count = consulta_existente['count'] + 1
            cursor.execute("""
                UPDATE consultas 
                SET count = %s 
                WHERE id = %s
            """, (nuevo_count, consulta_existente['id']))
        else:
            # Si no existe, crear nuevo registro
            cursor.execute("""
                INSERT INTO consultas (user_id, count)
                VALUES (%s, 1)
            """, (request.usuario['id_user'],))
        
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
    Headers: X-User-Celular: 3007471199
    """
    try:
        # Crear libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = "Plantilla Reportes"
        
        # Encabezados
        headers = [
            'Fecha_Reporte', 'Numero_Documento', 'Nombres', 'Apellidos',
            'Fecha_cierre', 'Placa', 'Valor_Reporte', 'Descripcion_Reporte',
            'Vehiculo_afiliado', 'Estado'
        ]
        
        # Estilo de encabezados
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Fila de ejemplo
        ejemplo = [
            '2024-01-15', '1234567890', 'JUAN', 'PEREZ GOMEZ',
            '', 'ABC123', '50000', 'REPORTE NEGATIVO POR TARIFAS',
            'ADMICARS', 'ACTIVA'
        ]
        
        for col, valor in enumerate(ejemplo, 1):
            ws.cell(row=2, column=col, value=valor)
        
        # Ajustar anchos de columna
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column].width = max_length + 2
        
        # Guardar en memoria
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
    Importar datos masivos desde Excel
    Headers: X-User-Celular: 3007471199
    Form-data: file (archivo Excel)
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
        # Leer Excel
        df = pd.read_excel(file)
        
        # Validar columnas requeridas
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
                    request.usuario['id_user']  # Usuario que subió el registro
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
            'detalle_errores': errores[:10]  # Primeros 10 errores
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
    Headers: X-User-Celular: 3007471199
    Body: {
        "numero_documento": "1234567890",
        "nombres": "JUAN",
        "apellidos": "PEREZ",
        "placa": "ABC123",
        "valor_reporte": 50000,
        "descripcion": "REPORTE NEGATIVO POR TARIFAS",
        "vehiculo_afiliado": "ADMICARS",
        "estado": "ACTIVA"
    }
    """
    data = request.get_json()
    
    # Validar campos requeridos
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
    Headers: X-User-Celular: 3007471199
    Body: { campos a actualizar }
    """
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verificar permisos
        cursor.execute("""
            SELECT Reportante_Nombres FROM personas WHERE id = %s
        """, (id,))
        
        reporte = cursor.fetchone()
        
        if not reporte:
            return jsonify({
                'success': False,
                'message': 'Reporte no encontrado'
            }), 404
        
        # Verificar si es admin o creador
        es_admin = request.usuario['rol'] == 'admin'
        es_creador = str(reporte['Reportante_Nombres']) == str(request.usuario['id_user'])
        
        if not (es_admin or es_creador):
            return jsonify({
                'success': False,
                'message': 'No tiene permisos para editar este reporte'
            }), 403
        
        # Construir query dinámico
        campos_permitidos = [
            'Nombres', 'Apellidos', 'Placa', 'Valor_Reporte',
            'Descripcion_Reporte', 'Estado', 'Fecha_cierre'
        ]
        
        campos_actualizar = []
        valores = []
        
        for campo in campos_permitidos:
            if campo.lower().replace('_', '') in [k.lower().replace('_', '') for k in data.keys()]:
                campos_actualizar.append(f"{campo} = %s")
                valores.append(data.get(campo.lower(), data.get(campo)))
        
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

# ==================== RUTA DE PRUEBA ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Verificar que la API está funcionando
    ---
    tags:
      - Health
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
    """
    return jsonify({
        'success': True,
        'message': 'API InfoTaxi funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== INICIAR SERVIDOR ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
