"""
API REST para Sistema InfoTaxi
Servicios de gestión de usuarios y reportes
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
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
    data = request.get_json()
    celular = data.get('celular')
    
    if not celular:
        return jsonify({'success': False, 'message': 'Número de celular requerido'}), 400
    
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
    data = request.get_json()

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
        
        cursor.execute("SELECT id_user FROM users WHERE Celular = %s OR username = %s",
                      (data['celular'], data['username']))
        if cursor.fetchone():
            return jsonify({
                'success': False,
                'message': 'Ya existe un usuario con ese celular o email'
            }), 409
        
        password_hash = hashlib.sha1(data['password'].encode()).hexdigest()
        
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


# ==================== SERVICIO 3: CONSULTAR PERSONA ====================
@app.route('/api/personas/<cedula>', methods=['GET'])
@verificar_usuario
def consultar_persona(cedula):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Error de conexión'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
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
        
        cursor.execute("""
            INSERT INTO consultas (user_id, count)
            VALUES (%s, 1)
        """, (request.usuario['id_user'],))
        conn.commit()
        
        result = []
        for r in reportes:
            result.append({
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
            'reportes': result
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


# ==================== SERVICIO 5: IMPORTAR EXCEL ====================
@app.route('/api/importar-excel', methods=['POST'])
@verificar_usuario
def importar_excel():

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se proporcionó archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Archivo vacío'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'success': False, 'message': 'Formato no válido'}), 400
    
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

    data = request.get_json()
    
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

    data = request.get_json()
    
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
            return jsonify({'success': False, 'message': 'Reporte no encontrado'}), 404
        
        es_admin = request.usuario['rol'] == 'admin'
        es_creador = str(reporte['Reportante_Nombres']) == str(request.usuario['id_user'])
        
        if not (es_admin or es_creador):
            return jsonify({'success': False, 'message': 'No tiene permisos'}), 403
        
        campos_permitidos = [
            'Nombres', 'Apellidos', 'Placa', 'Valor_Reporte',
            'Descripcion_Reporte', 'Estado', 'Fecha_cierre'
        ]
        
        campos_actualizar = []
        valores = []
        
        for campo in campos_permitidos:
            if campo.lower() in data.keys() or campo in data.keys():
                campos_actualizar.append(f"{campo} = %s")
                valores.append(data.get(campo.lower(), data.get(campo)))
        
        if not campos_actualizar:
            return jsonify({'success': False, 'message': 'Nada para actualizar'}), 400
        
        valores.append(id)
        query = f"UPDATE personas SET {', '.join(campos_actualizar)} WHERE id = %s"
        
        cursor.execute(query, valores)
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Reporte actualizado exitosamente'}), 200
        
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
    return jsonify({
        'success': True,
        'message': 'API InfoTaxi funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    }), 200


# ==================== INICIAR SERVIDOR ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
