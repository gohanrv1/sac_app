from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger
import mysql.connector
from mysql.connector import Error
from datetime import datetime

########################################
# CONFIGURACIÓN DE BASE DE DATOS
########################################
DB_CONFIG = {
    'host': '31.97.130.20',
    'port': 4646,
    'database': 'electo',
    'user': 'mariadb',
    'password': '9204a8246f7ed4fe49e6'
}

########################################
# CREAR APP
########################################
app = Flask(__name__)

# CORS global
CORS(app, resources={r"/*": {"origins": "*"}})

########################################
# SWAGGER
########################################
app.config['SWAGGER'] = {
    "title": "InfoTaxi API",
    "uiversion": 3
}
swagger = Swagger(app)


########################################
# FUNCIÓN DE CONEXIÓN (AUTO-RECONNECT)
########################################
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print("❌ Error de conexión MySQL:", e)
    return None


########################################
# FORMATO UNIFORME DE RESPUESTAS
########################################
def success(message, data=None):
    return jsonify({"ok": True, "message": message, "data": data})

def error(message, code=400):
    return jsonify({"ok": False, "error": message}), code


########################################
# HEALTH CHECK
########################################
@app.route('/api/health', methods=['GET'])
def health():
    conn = get_connection()
    if conn:
        conn.close()
        return success("OK", {"database": "connected"})
    return error("Database not connected", 500)


########################################
# GET DATOS DE TAXISTA
########################################
@app.route('/api/taxista/<placa>', methods=['GET'])
def get_taxista(placa):
    """
    Obtener información del taxista por placa
    ---
    parameters:
      - name: placa
        in: path
        required: true
        type: string
    responses:
      200:
        description: Información del taxista
    """
    conn = get_connection()
    if not conn:
        return error("No hay conexión a la base de datos", 500)

    try:
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT *
            FROM infosac_taxis
            WHERE placa = %s
            LIMIT 1
        """
        cursor.execute(query, (placa,))
        row = cursor.fetchone()

        if not row:
            return error("No existe registro para esta placa", 404)

        return success("Registro encontrado", row)

    except Exception as e:
        return error(str(e), 500)

    finally:
        conn.close()


########################################
# GUARDAR POSICIÓN GPS
########################################
@app.route('/api/posicion', methods=['POST'])
def save_posicion():
    """
    Guardar posición de taxi
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: posicion
          required:
            - placa
            - lat
            - lng
          properties:
            placa:
              type: string
            lat:
              type: number
            lng:
              type: number
    responses:
      200:
        description: Posición guardada
    """
    data = request.get_json()

    if not data:
        return error("JSON inválido")

    placa = data.get("placa")
    lat = data.get("lat")
    lng = data.get("lng")

    if not placa or lat is None or lng is None:
        return error("Faltan campos obligatorios: placa, lat, lng")

    conn = get_connection()
    if not conn:
        return error("No hay conexión a la base de datos", 500)

    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO infosac_posiciones (placa, lat, lng, fecha)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (placa, lat, lng, datetime.now()))
        conn.commit()

        return success("Posición guardada correctamente")

    except Exception as e:
        return error(str(e), 500)

    finally:
        conn.close()


########################################
# INICIO
########################################
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
